from app.database import SessionLocal, ExchangeRate

db = SessionLocal()
try:
    total = db.query(ExchangeRate).count()
    print(f"📊 Всего записей: {total}")

    # Примеры данных
    samples = db.query(ExchangeRate).filter(
        ExchangeRate.currency.in_(["USD", "EUR"])
    ).order_by(ExchangeRate.date).limit(5).all()

    print("\n📌 Примеры записей:")
    for s in samples:
        print(f"   {s.date} | {s.currency}: {s.rate} CZK")

finally:
    db.close()