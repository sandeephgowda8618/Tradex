from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from app.services.fundamental_engine import FundamentalEngine
from app.services.technical_engine import TechnicalEngine
from app.tasks.llm_tasks import generate_llm_analysis
from app.utils.cache import RedisCache
from app.utils.logger import get_logger


class AnalysisOrchestrator:
    TECHNICAL_API_MAP: Dict[str, Dict[str, Any]] = {
        "rsi": {
            "function": "RSI",
            "interval": "daily",
            "params": {"time_period": 14, "series_type": "close"},
        },
        "macd": {
            "function": "MACD",
            "interval": "daily",
            "params": {"series_type": "close"},
        },
        "sma_50": {
            "function": "SMA",
            "interval": "daily",
            "params": {"time_period": 50, "series_type": "close"},
        },
        "sma_200": {
            "function": "SMA",
            "interval": "daily",
            "params": {"time_period": 200, "series_type": "close"},
        },
        "ema_20": {
            "function": "EMA",
            "interval": "daily",
            "params": {"time_period": 20, "series_type": "close"},
        },
        "stoch": {
            "function": "STOCH",
            "interval": "daily",
            "params": {},
        },
        "obv": {
            "function": "OBV",
            "interval": "daily",
            "params": {},
        },
        "atr": {
            "function": "ATR",
            "interval": "daily",
            "params": {"time_period": 14},
        },
        "bbands": {
            "function": "BBANDS",
            "interval": "daily",
            "params": {"time_period": 20, "series_type": "close"},
        },
    }

    TTL_DAILY = 3600
    TTL_TECHNICAL = 3600
    TTL_FUNDAMENTAL = 3600
    TTL_COMBINED = 1200
    TTL_LLM = 86400

    def __init__(
        self,
        alpha_service: Any,
        cache: Optional[RedisCache] = None,
        request_delay_seconds: float = 12.0,
    ) -> None:
        self.alpha_service = alpha_service
        self.cache = cache
        self.request_delay_seconds = request_delay_seconds
        self.logger = get_logger(self.__class__.__name__)

    def _validate_symbol(self, symbol: str) -> None:
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("Symbol must be a non-empty string.")

    def _hash_selection(self, selection: Optional[List[str]]) -> str:
        if not selection:
            return "all"
        payload = json.dumps(sorted(selection), separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    def _market_key(self, symbol: str, function_name: str, params: Dict[str, Any]) -> str:
        params_payload = json.dumps(params, separators=(",", ":"), ensure_ascii=True)
        params_hash = hashlib.sha256(params_payload.encode("utf-8")).hexdigest()[:12]
        return f"market:{symbol}:{function_name}:{params_hash}"

    def _analysis_key(self, symbol: str, fundamentals: Optional[List[str]], technicals: Optional[List[str]]) -> str:
        return f"analysis:{symbol}:{self._hash_selection(fundamentals)}:{self._hash_selection(technicals)}"

    def _cached_or_fetch(self, cache_key: str, ttl_seconds: int, fetch_fn: Any) -> Dict[str, Any]:
        if self.cache:
            cached = self.cache.get_json(cache_key)
            if cached is not None:
                self.logger.info("Cache hit | key=%s", cache_key)
                return cached
            self.logger.info("Cache miss | key=%s", cache_key)
        result = fetch_fn()
        if self.cache:
            self.cache.set_json(cache_key, result, ttl_seconds)
        if self.request_delay_seconds > 0:
            time.sleep(self.request_delay_seconds)
        return result

    def analyze(
        self,
        symbol: str,
        selected_fundamentals: Optional[List[str]] = None,
        selected_technicals: Optional[List[str]] = None,
        include_llm: bool = False,
        analysis_result_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._validate_symbol(symbol)
        start_time = time.time()
        self.logger.info("Starting analysis | symbol=%s", symbol)

        fundamentals_requested = selected_fundamentals is None or bool(selected_fundamentals)
        technicals_requested = selected_technicals is None or bool(selected_technicals)

        if self.cache and (fundamentals_requested or technicals_requested):
            combined_key = self._analysis_key(symbol, selected_fundamentals, selected_technicals)
            cached_combined = self.cache.get_json(combined_key)
            if cached_combined is not None:
                self.logger.info("Cache hit | symbol=%s", symbol)
                return cached_combined
        else:
            combined_key = None

        overview = {}
        income = {}
        balance = {}
        cash_flow = {}
        earnings = {}
        daily_series = {}
        technical_payloads: Dict[str, Dict[str, Any]] = {}

        if fundamentals_requested:
            overview = self._cached_or_fetch(
                self._market_key(symbol, "OVERVIEW", {}),
                self.TTL_FUNDAMENTAL,
                lambda: self.alpha_service.get_overview(symbol),
            )
            income = self._cached_or_fetch(
                self._market_key(symbol, "INCOME_STATEMENT", {}),
                self.TTL_FUNDAMENTAL,
                lambda: self.alpha_service.get_income_statement(symbol),
            )
            balance = self._cached_or_fetch(
                self._market_key(symbol, "BALANCE_SHEET", {}),
                self.TTL_FUNDAMENTAL,
                lambda: self.alpha_service.get_balance_sheet(symbol),
            )
            cash_flow = self._cached_or_fetch(
                self._market_key(symbol, "CASH_FLOW", {}),
                self.TTL_FUNDAMENTAL,
                lambda: self.alpha_service.get_cash_flow(symbol),
            )
            earnings = self._cached_or_fetch(
                self._market_key(symbol, "EARNINGS", {}),
                self.TTL_FUNDAMENTAL,
                lambda: self.alpha_service.get_earnings(symbol),
            )

        technical_keys: List[str] = []
        if technicals_requested:
            technical_keys = (
                list(self.TECHNICAL_API_MAP.keys()) if selected_technicals is None else selected_technicals
            )
            allowed = set(self.TECHNICAL_API_MAP.keys()) | {"volume_spike"}
            invalid = [k for k in technical_keys if k not in allowed]
            if invalid:
                raise ValueError(f"Invalid technical indicators: {invalid}")

            if technical_keys:
                daily_series = self._cached_or_fetch(
                    self._market_key(symbol, "TIME_SERIES_DAILY", {}),
                    self.TTL_DAILY,
                    lambda: self.alpha_service.get_daily_series(symbol),
                )

            for key in technical_keys:
                config = self.TECHNICAL_API_MAP.get(key)
                if not config:
                    continue
                interval = config.get("interval", "daily")
                params = dict(config.get("params", {}))
                params_with_interval = {"interval": interval, **params}
                cache_key = self._market_key(symbol, config["function"], params_with_interval)
                technical_payloads[key] = self._cached_or_fetch(
                    cache_key,
                    self.TTL_TECHNICAL,
                    lambda k=config["function"], i=interval, p=params: self.alpha_service.get_technical_indicator(
                        k, symbol, interval=i, extra_params=p
                    ),
                )

        fundamental_result = None
        if fundamentals_requested:
            fundamental_engine = FundamentalEngine(
                overview=overview,
                income_statement=income,
                balance_sheet=balance,
                cash_flow=cash_flow,
                earnings=earnings,
            )
            fundamental_result = fundamental_engine.analyze(selected_metrics=selected_fundamentals)

        technical_result = None
        if technicals_requested and technical_keys:
            technical_engine = TechnicalEngine(
                daily_series=daily_series,
                rsi_data=technical_payloads.get("rsi", {}),
                macd_data=technical_payloads.get("macd", {}),
                sma_50=technical_payloads.get("sma_50", {}),
                sma_200=technical_payloads.get("sma_200", {}),
                ema_20=technical_payloads.get("ema_20", {}),
                stoch_data=technical_payloads.get("stoch", {}),
                obv_data=technical_payloads.get("obv", {}),
                atr_data=technical_payloads.get("atr", {}),
                bbands_data=technical_payloads.get("bbands", {}),
            )
            technical_result = technical_engine.analyze(selected_indicators=technical_keys)

        combined = self._combine_scores(fundamental_result, technical_result)
        self.logger.info(
            "Deterministic analysis completed | symbol=%s | fundamental_score=%s | technical_score=%s",
            symbol,
            combined.get("fundamental_score"),
            combined.get("technical_score"),
        )

        llm_output = None
        if include_llm:
            llm_payload = self._build_llm_payload(symbol, fundamental_result, technical_result, combined)
            llm_key = self._llm_key(symbol, llm_payload)
            if self.cache:
                cached_llm = self.cache.get_json(llm_key)
                if cached_llm is not None:
                    llm_output = cached_llm
            if llm_output is None:
                if analysis_result_id:
                    self.logger.info("Queueing LLM task | analysis_result_id=%s", analysis_result_id)
                    generate_llm_analysis.delay(analysis_result_id, llm_payload)
                    llm_output = {"status": "queued"}
                else:
                    self.logger.info("LLM skipped | analysis_result_id missing")
                    llm_output = {"status": "skipped", "reason": "analysis_result_id_required"}

        result = {
            "symbol": symbol.upper(),
            "fundamental_analysis": fundamental_result,
            "technical_analysis": technical_result,
            "combined_analysis": combined,
            "llm_interpretation": llm_output,
        }

        if self.cache and combined_key:
            self.cache.set_json(combined_key, result, self.TTL_COMBINED)

        self.logger.info(
            "Analysis completed in %.2fs | symbol=%s", time.time() - start_time, symbol
        )
        return result

    def _combine_scores(
        self,
        fundamental_result: Optional[Dict[str, Any]],
        technical_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        fundamental_score = None
        technical_score = None
        if fundamental_result:
            fundamental_score = fundamental_result.get("overall_score")
        if technical_result:
            technical_score = technical_result.get("overall_technical_score")

        if fundamental_score is None and technical_score is None:
            return {"overall_score": None, "investment_bias": "Neutral", "confidence": "Low"}

        if fundamental_score is None:
            overall = technical_score
        elif technical_score is None:
            overall = fundamental_score
        else:
            overall = (0.6 * fundamental_score) + (0.4 * technical_score)

        if overall is None:
            bias = "Neutral"
        elif overall >= 7.5:
            bias = "Strong Bullish"
        elif overall >= 6.0:
            bias = "Bullish"
        elif overall >= 4.0:
            bias = "Neutral"
        else:
            bias = "Bearish"

        if fundamental_score is not None and technical_score is not None:
            confidence = "High"
        elif fundamental_score is not None or technical_score is not None:
            confidence = "Medium"
        else:
            confidence = "Low"

        return {
            "overall_score": overall,
            "fundamental_score": fundamental_score,
            "technical_score": technical_score,
            "investment_bias": bias,
            "confidence": confidence,
        }

    def _build_llm_payload(
        self,
        symbol: str,
        fundamental_result: Optional[Dict[str, Any]],
        technical_result: Optional[Dict[str, Any]],
        combined: Dict[str, Any],
    ) -> Dict[str, Any]:
        fundamentals = fundamental_result or {}
        technicals = technical_result or {}

        def _top_keys(scores: Dict[str, Any], top_n: int, reverse: bool = True) -> List[str]:
            items = []
            for key, val in scores.items():
                if val is None:
                    continue
                items.append((key, val))
            items.sort(key=lambda x: x[1], reverse=reverse)
            return [k for k, _ in items[:top_n]]

        category_scores = fundamentals.get("category_scores", {}) if fundamentals else {}
        top_strengths = _top_keys(category_scores, 3, reverse=True)
        weaknesses = _top_keys(category_scores, 3, reverse=False)

        return {
            "symbol": symbol.upper(),
            "overall_score": combined.get("overall_score"),
            "fundamental_score": fundamentals.get("overall_score"),
            "technical_score": technicals.get("overall_technical_score"),
            "fundamental": {
                "profitability": category_scores.get("profitability"),
                "growth": category_scores.get("growth"),
                "financial_strength": category_scores.get("financial_strength"),
                "valuation": category_scores.get("valuation"),
                "risk_level": fundamentals.get("risk", {}).get("level"),
                "top_strengths": top_strengths,
                "weaknesses": weaknesses,
            },
            "technical": {
                "trend_direction": technicals.get("trend_direction"),
                "momentum_strength": technicals.get("momentum_strength"),
                "volatility": technicals.get("volatility_level"),
                "entry_signal": technicals.get("entry_signal"),
            },
        }

    def _llm_key(self, symbol: str, payload: Dict[str, Any]) -> str:
        payload_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
        payload_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()[:12]
        return f"llm:{symbol}:{payload_hash}"
