from pydantic_settings import BaseSettings, SettingsConfigDict
import json

class Settings(BaseSettings):
    db_url: str = "sqlite:///./cnb_rates.db"
    sync_interval_minutes: int = 1
    currencies: list[str] = ["USD", "EUR"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @staticmethod
    def parse_currencies(currencies_str: str) -> list[str]:
        try:
            return json.loads(currencies_str)
        except (json.JSONDecodeError, TypeError):
            return []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if isinstance(self.currencies, str):
            self.currencies = self.parse_currencies(self.currencies)

settings = Settings()