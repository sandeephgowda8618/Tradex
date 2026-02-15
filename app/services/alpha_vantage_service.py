from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class AlphaVantageService:
    def __init__(self, api_key: str, base_url: str = "https://www.alphavantage.co/query") -> None:
        self.api_key = api_key
        self.base_url = base_url

    def _make_request(
        self,
        function_name: str,
        symbol: str,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "function": function_name,
            "symbol": symbol,
            "apikey": self.api_key,
        }
        if extra_params:
            params.update(extra_params)

        response = requests.get(self.base_url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    # Fundamental data
    def get_overview(self, symbol: str) -> Dict[str, Any]:
        return self._make_request("OVERVIEW", symbol)

    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        return self._make_request("INCOME_STATEMENT", symbol)

    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        return self._make_request("BALANCE_SHEET", symbol)

    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        return self._make_request("CASH_FLOW", symbol)

    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        return self._make_request("EARNINGS", symbol)

    # Core stock data
    def get_daily_series(self, symbol: str) -> Dict[str, Any]:
        return self._make_request("TIME_SERIES_DAILY", symbol)

    # Technical indicators
    def get_technical_indicator(
        self,
        function_name: str,
        symbol: str,
        interval: str = "daily",
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"interval": interval}
        if extra_params:
            params.update(extra_params)
        return self._make_request(function_name, symbol, params)
