import requests
import csv
from io import StringIO
from datetime import datetime
from app.database import SessionLocal, ExchangeRate, Base, engine
from app.config import settings


def parse_cnb_data(text: str, target_currencies: list[str]) -> list[dict]:
    reader = csv.reader(StringIO(text), delimiter='|')
    rows = list(reader)

    if len(rows) < 2:
        return []

    # Парсим заголовки: "1 USD" → "USD"
    headers = [h.strip().split()[-1] for h in rows[0][1:]]

    results = []
    for row in rows[1:]:
        if not row or not row[0].strip():
            continue

        # Парсим дату: "02.01.2019" → date(2019, 1, 2)
        try:
            date_obj = datetime.strptime(row[0].strip(), "%d.%m.%Y").date()
        except ValueError:
            continue

        # Сопоставляем валюты с курсами
        for i, currency in enumerate(headers, start=1):
            if currency in target_currencies and i < len(row) and row[i].strip():
                try:
                    results.append({
                        "currency": currency,
                        "rate": float(row[i]),
                        "date": date_obj
                    })
                except (ValueError, IndexError):
                    continue

    return results


def import_year(year: int, currencies: list[str] = None):
    """Импортирует данные за указанный год"""
    if currencies is None:
        currencies = settings.currencies

    url = f"https://www.cnb.cz/en/financial_markets/foreign_exchange_market/exchange_rate_fixing/year.txt?year={year}"

    print(f"📥 Скачиваю данные за {year} год...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Ошибка загрузки: {e}")
        return

    print(f"🔍 Парсим данные для валют: {currencies}...")
    records = parse_cnb_data(response.text, currencies)
    print(f"   Найдено записей: {len(records)}")

    if not records:
        print("⚠️ Нет данных для импорта")
        return

    # Создаём таблицы, если нет (на всякий случай)
    Base.metadata.create_all(bind=engine)

    # Сохраняем в БД
    db = SessionLocal()
    saved = 0
    try:
        for record in records:
            # Проверяем на дубликаты
            exists = db.query(ExchangeRate).filter(
                ExchangeRate.currency == record["currency"],
                ExchangeRate.date == record["date"]
            ).first()

            if not exists:
                db.add(ExchangeRate(**record))
                saved += 1

        db.commit()
        print(f"✅ Сохранено {saved} новых записей в cnb_rates.db")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка сохранения: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Импортируем данные за 2019 год
    import_year(2019)