import yfinance as yf

from datetime import datetime, timedelta


class AssetTicker:
    def __init__(self, ticker: str) -> yf.Ticker:
        if not isinstance(ticker, str):
            raise TypeError(f"Expected a string for ticker, got {type(ticker).__name__}")
        self.asset = yf.Ticker(ticker)

    def get_current_price(self) -> float:
        return round(self.asset.history(period="1d")["Close"].iloc[-1], 2)

    def get_long_name(self) -> str:
        return self.asset.info.get("longName", "Unknown Asset")

    def get_previous_price(self, date: datetime) -> yf.Ticker:
        return round(
            self.asset.history(start=date, end=date + timedelta(days=1))["Close"].iloc[
                -1
            ],
            2,
        )
