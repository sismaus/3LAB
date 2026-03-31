from sqlalchemy import create_engine, Column, Integer, String, Float, Date, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

Base = declarative_base()

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String(3), nullable=False, index=True)  # USD, EUR, GBP...
    rate = Column(Float, nullable=False)  # Курс к чешской кроне (CZK)
    date = Column(Date, nullable=False, index=True)  # Дата

    # Уникальность: одна запись на валюту + дату
    __table_args__ = (
        UniqueConstraint('currency', 'date', name='uq_currency_date'),
    )

    def __repr__(self):
        return f"<ExchangeRate(currency={self.currency}, rate={self.rate}, date={self.date})>"


connect_args = {"check_same_thread": False} if settings.db_url.startswith("sqlite") else {}

engine = create_engine(settings.db_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    print(f"🔗 Подключение к: {settings.db_url}")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно!")


def drop_all_tables():
    Base.metadata.drop_all(bind=engine)
    print("🗑️ Все таблицы удалены")