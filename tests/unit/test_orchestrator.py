from app.services.analysis_orchestrator import AnalysisOrchestrator
from tests.unit.test_fundamental_engine import _fundamental_strong
from tests.unit.test_technical_engine import _technical_bullish


class FakeAlpha:
    def __init__(self, fundamental: dict, technical: dict):
        self.fundamental = fundamental
        self.technical = technical

    def get_overview(self, symbol):
        return self.fundamental["overview"]

    def get_income_statement(self, symbol):
        return self.fundamental["income_statement"]

    def get_balance_sheet(self, symbol):
        return self.fundamental["balance_sheet"]

    def get_cash_flow(self, symbol):
        return self.fundamental["cash_flow"]

    def get_earnings(self, symbol):
        return self.fundamental["earnings"]

    def get_daily_series(self, symbol):
        return self.technical["daily_series"]

    def get_technical_indicator(self, function_name, symbol, interval="daily", extra_params=None):
        if function_name == "RSI":
            return self.technical["rsi"]
        if function_name == "MACD":
            return self.technical["macd"]
        if function_name == "SMA":
            if extra_params and extra_params.get("time_period") == 50:
                return self.technical["sma_50"]
            return self.technical["sma_200"]
        if function_name == "EMA":
            return self.technical["ema_20"]
        if function_name == "STOCH":
            return self.technical["stoch"]
        if function_name == "OBV":
            return self.technical["obv"]
        if function_name == "ATR":
            return self.technical["atr"]
        if function_name == "BBANDS":
            return self.technical["bbands"]
        return {}


def test_orchestrator_with_mocked_service():
    fundamental = _fundamental_strong()
    technical = _technical_bullish()

    orchestrator = AnalysisOrchestrator(alpha_service=FakeAlpha(fundamental, technical), cache=None, request_delay_seconds=0)
    result = orchestrator.analyze("AAPL", include_llm=False)

    assert result["combined_analysis"]["overall_score"] is not None
    assert result["fundamental_analysis"]["overall_score"] >= 6.5
