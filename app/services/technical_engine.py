from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class TechnicalEngine:
    def __init__(
        self,
        daily_series: Dict[str, Any],
        rsi_data: Dict[str, Any],
        macd_data: Dict[str, Any],
        sma_50: Dict[str, Any],
        sma_200: Dict[str, Any],
        ema_20: Dict[str, Any],
        stoch_data: Dict[str, Any],
        obv_data: Dict[str, Any],
        atr_data: Dict[str, Any],
        bbands_data: Dict[str, Any],
    ) -> None:
        self.daily_series = daily_series or {}
        self.rsi_data = rsi_data or {}
        self.macd_data = macd_data or {}
        self.sma_50 = sma_50 or {}
        self.sma_200 = sma_200 or {}
        self.ema_20 = ema_20 or {}
        self.stoch_data = stoch_data or {}
        self.obv_data = obv_data or {}
        self.atr_data = atr_data or {}
        self.bbands_data = bbands_data or {}

    def _to_float(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped in {"", "None", "null", "N/A"}:
                return None
            try:
                return float(stripped)
            except ValueError:
                return None
        return None

    def _extract_time_series(self, series: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        if "Time Series (Daily)" in series:
            return series.get("Time Series (Daily)", {}) or {}
        if "Time Series (Daily) " in series:
            return series.get("Time Series (Daily) ", {}) or {}
        for key, value in series.items():
            if isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):
                return value
        return {}

    def _sorted_dates(self, data: Dict[str, Any]) -> List[str]:
        return sorted(data.keys(), reverse=True)

    def _extract_price_series(self) -> List[Dict[str, Any]]:
        series = self._extract_time_series(self.daily_series)
        dates = self._sorted_dates(series)
        price_series = []
        for date in dates:
            row = series.get(date, {})
            price_series.append(
                {
                    "date": date,
                    "close": self._to_float(row.get("4. close")),
                    "high": self._to_float(row.get("2. high")),
                    "low": self._to_float(row.get("3. low")),
                    "volume": self._to_float(row.get("5. volume")),
                }
            )
        return price_series

    def _extract_indicator_series(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        for key, value in data.items():
            if key.startswith("Technical Analysis") and isinstance(value, dict):
                return value
        for key, value in data.items():
            if isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):
                return value
        return {}

    def _latest_indicator_value(
        self, data: Dict[str, Any], field: str
    ) -> Tuple[Optional[float], Optional[float]]:
        series = self._extract_indicator_series(data)
        dates = self._sorted_dates(series)
        if not dates:
            return None, None
        latest = self._to_float(series[dates[0]].get(field))
        previous = None
        if len(dates) > 1:
            previous = self._to_float(series[dates[1]].get(field))
        return latest, previous

    def _latest_indicator_fields(
        self, data: Dict[str, Any], fields: List[str]
    ) -> Tuple[Dict[str, Optional[float]], Dict[str, Optional[float]]]:
        series = self._extract_indicator_series(data)
        dates = self._sorted_dates(series)
        latest_values: Dict[str, Optional[float]] = {f: None for f in fields}
        previous_values: Dict[str, Optional[float]] = {f: None for f in fields}
        if not dates:
            return latest_values, previous_values
        latest_row = series.get(dates[0], {})
        for field in fields:
            latest_values[field] = self._to_float(latest_row.get(field))
        if len(dates) > 1:
            prev_row = series.get(dates[1], {})
            for field in fields:
                previous_values[field] = self._to_float(prev_row.get(field))
        return latest_values, previous_values

    def _trend_context(
        self,
        price: Optional[float],
        sma_50: Optional[float],
        sma_200: Optional[float],
        ema_20: Optional[float],
    ) -> Dict[str, Any]:
        if price is None or sma_50 is None or sma_200 is None:
            return {"direction": "Unknown", "score": None, "signal": "Insufficient data"}

        direction = "Sideways"
        if price > sma_200 and sma_50 > sma_200:
            direction = "Uptrend"
        elif price < sma_200 and sma_50 < sma_200:
            direction = "Downtrend"

        if sma_50 > sma_200:
            signal = "Golden Cross"
        elif sma_50 < sma_200:
            signal = "Death Cross"
        else:
            signal = "Neutral Cross"

        return {"direction": direction, "signal": signal}

    def _linear_regression_slope(self, values: List[Optional[float]]) -> Optional[float]:
        data = [v for v in values if v is not None]
        if len(data) < 5:
            return None
        n = len(data)
        x_vals = list(range(n))
        x_mean = sum(x_vals) / n
        y_mean = sum(data) / n
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, data))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)
        if denominator == 0:
            return None
        return numerator / denominator

    def _rsi_signal(self, rsi: Optional[float], trend_direction: str) -> Dict[str, Any]:
        if rsi is None:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        if rsi < 30:
            regime = "Oversold"
        elif rsi < 50:
            regime = "Weak"
        elif rsi <= 70:
            regime = "Bullish"
        else:
            regime = "Overbought"

        base_score = max(0.0, min(10.0, (rsi / 100.0) * 10.0))
        if trend_direction == "Uptrend" and 60 <= rsi <= 70:
            base_score += 1.0
        if trend_direction == "Downtrend" and rsi >= 60:
            base_score -= 1.0
        if rsi > 70:
            base_score -= 1.0
        if rsi < 30:
            base_score += 1.0

        score = max(0.0, min(10.0, base_score))
        signal = f"RSI {regime}"
        return {"value": rsi, "signal": signal, "score": score, "regime": regime}

    def _macd_signal(self) -> Dict[str, Any]:
        latest, prev = self._latest_indicator_fields(
            self.macd_data, ["MACD", "MACD_Signal", "MACD_Hist"]
        )
        macd = latest["MACD"]
        signal_line = latest["MACD_Signal"]
        hist = latest["MACD_Hist"]
        prev_macd = prev["MACD"]
        prev_signal = prev["MACD_Signal"]
        prev_hist = prev["MACD_Hist"]

        if macd is None or signal_line is None:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        bullish_cross = prev_macd is not None and prev_signal is not None and macd > signal_line and prev_macd <= prev_signal
        bearish_cross = prev_macd is not None and prev_signal is not None and macd < signal_line and prev_macd >= prev_signal
        hist_rising = hist is not None and prev_hist is not None and hist > prev_hist

        score = 5.0
        regime = "Neutral"
        if bullish_cross:
            score += 2.5
            regime = "Bullish Crossover"
        if bearish_cross:
            score -= 2.5
            regime = "Bearish Crossover"
        if hist is not None and hist > 0:
            score += 1.0
        if hist_rising:
            score += 0.5
        if hist is not None and hist < 0:
            score -= 0.5

        score = max(0.0, min(10.0, score))
        signal = regime
        return {
            "value": {"macd": macd, "signal": signal_line, "hist": hist},
            "signal": signal,
            "score": score,
            "regime": regime,
        }

    def _stoch_signal(self) -> Dict[str, Any]:
        latest, _prev = self._latest_indicator_fields(self.stoch_data, ["SlowK", "SlowD"])
        slow_k = latest["SlowK"]
        slow_d = latest["SlowD"]
        if slow_k is None:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        if slow_k < 20:
            regime = "Oversold"
            score = 7.0
        elif slow_k < 50:
            regime = "Weak"
            score = 4.5
        elif slow_k <= 80:
            regime = "Bullish"
            score = 6.5
        else:
            regime = "Overbought"
            score = 4.0

        signal = regime
        return {
            "value": {"slow_k": slow_k, "slow_d": slow_d},
            "signal": signal,
            "score": score,
            "regime": regime,
        }

    def _obv_trend(self, price_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        obv_latest, obv_prev = self._latest_indicator_value(self.obv_data, "OBV")
        if obv_latest is None:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        obv_series = self._extract_indicator_series(self.obv_data)
        dates = self._sorted_dates(obv_series)
        values = [self._to_float(obv_series[d].get("OBV")) for d in dates[:5]]
        values = [v for v in values if v is not None]

        obv_up = False
        if len(values) >= 2 and values[0] is not None and values[-1] is not None:
            obv_up = values[0] > values[-1]

        price_up = False
        if len(price_series) >= 2 and price_series[0]["close"] is not None and price_series[1]["close"] is not None:
            price_up = price_series[0]["close"] > price_series[1]["close"]

        score = 5.0
        regime = "Neutral"
        if obv_up and price_up:
            score += 2.0
            regime = "Confirmation"
        elif obv_up and not price_up:
            score += 1.0
            regime = "Accumulation"
        elif not obv_up and price_up:
            score -= 2.0
            regime = "Distribution"
        else:
            score -= 0.5
            regime = "Weak"

        score = max(0.0, min(10.0, score))
        return {
            "value": obv_latest,
            "signal": regime,
            "score": score,
            "regime": regime,
        }

    def _volume_spike(self, price_series: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not price_series:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        latest_volume = price_series[0].get("volume")
        volumes = [row.get("volume") for row in price_series[:20] if row.get("volume") is not None]
        if latest_volume is None or len(volumes) < 5:
            return {"value": latest_volume, "signal": "Insufficient data", "score": None, "regime": None}

        avg_volume = sum(volumes) / len(volumes)
        ratio = latest_volume / avg_volume if avg_volume else None
        if ratio is None:
            return {"value": latest_volume, "signal": "Insufficient data", "score": None, "regime": None}

        score = min(10.0, max(0.0, 5.0 + (ratio - 1.0) * 4.0))
        if ratio >= 1.8:
            regime = "High Spike"
        elif ratio >= 1.3:
            regime = "Moderate Spike"
        else:
            regime = "Normal"

        return {"value": ratio, "signal": regime, "score": score, "regime": regime}

    def _atr_regime(self, price: Optional[float]) -> Dict[str, Any]:
        atr, _prev = self._latest_indicator_value(self.atr_data, "ATR")
        if atr is None or price is None or price == 0:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        ratio = atr / price
        if ratio < 0.015:
            regime = "Low Volatility"
            score = 5.0
        elif ratio < 0.03:
            regime = "Moderate Volatility"
            score = 7.0
        else:
            regime = "High Volatility"
            score = 4.5

        return {"value": ratio, "signal": regime, "score": score, "regime": regime}

    def _bbands_signal(self, price: Optional[float]) -> Dict[str, Any]:
        latest, _prev = self._latest_indicator_fields(
            self.bbands_data, ["Real Upper Band", "Real Lower Band", "Real Middle Band"]
        )
        upper = latest["Real Upper Band"]
        lower = latest["Real Lower Band"]
        middle = latest["Real Middle Band"]
        if price is None or upper is None or lower is None or middle is None:
            return {"value": None, "signal": "Insufficient data", "score": None, "regime": None}

        bandwidth = (upper - lower) / middle if middle else None
        near_upper = price >= upper * 0.98
        near_lower = price <= lower * 1.02

        score = 5.0
        position = "Neutral"
        if near_lower:
            score = 7.0
            position = "Support Zone"
        elif near_upper:
            score = 4.0
            position = "Exhaustion Zone"

        volatility = "Normal"
        if bandwidth is not None and bandwidth < 0.05:
            volatility = "Squeeze"
            if price >= middle:
                score = 6.0

        return {
            "value": {"upper": upper, "lower": lower, "middle": middle, "bandwidth": bandwidth},
            "signal": {"position": position, "volatility": volatility},
            "score": score,
            "regime": {"position": position, "volatility": volatility},
        }

    def _avg_score(self, items: List[Dict[str, Any]]) -> Optional[float]:
        scores = [item.get("score") for item in items if item.get("score") is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)

    def analyze(self, selected_indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        selected = set(selected_indicators) if selected_indicators else None
        def include(name: str) -> bool:
            return selected is None or name in selected

        price_series = self._extract_price_series()
        latest_price = price_series[0]["close"] if price_series else None

        sma50, sma50_prev = self._latest_indicator_value(self.sma_50, "SMA")
        sma200, sma200_prev = self._latest_indicator_value(self.sma_200, "SMA")
        ema20, _ema20_prev = self._latest_indicator_value(self.ema_20, "EMA")

        trend_context = self._trend_context(latest_price, sma50, sma200, ema20)
        rsi_latest, _rsi_prev = self._latest_indicator_value(self.rsi_data, "RSI")

        indicators: Dict[str, Dict[str, Any]] = {}

        slope = self._linear_regression_slope([row["close"] for row in price_series[:20]])
        slope_direction = "Flat"
        if slope is not None:
            if slope > 0:
                slope_direction = "Up"
            elif slope < 0:
                slope_direction = "Down"

        if include("sma_50"):
            if sma50 is None or sma200 is None or latest_price is None:
                indicators["sma_50"] = {
                    "value": sma50,
                    "signal": "Insufficient data",
                    "score": None,
                    "regime": "Insufficient data",
                }
            else:
                indicators["sma_50"] = {
                    "value": sma50,
                    "signal": "Above 200"
                    if sma50 is not None and sma200 is not None and sma50 > sma200
                    else "Below 200",
                    "score": min(
                        10.0,
                        max(
                            0.0,
                            (3.0 if sma50 is not None and sma200 is not None and sma50 > sma200 else 0.0)
                            + (2.0 if latest_price is not None and sma50 is not None and latest_price > sma50 else 0.0)
                            + (1.0 if slope_direction == "Up" else 0.0),
                        ),
                    ),
                    "regime": trend_context["signal"],
                }
        if include("sma_200"):
            if sma200 is None or latest_price is None or sma50 is None:
                indicators["sma_200"] = {
                    "value": sma200,
                    "signal": "Insufficient data",
                    "score": None,
                    "regime": "Insufficient data",
                }
            else:
                indicators["sma_200"] = {
                    "value": sma200,
                    "signal": "Price Above"
                    if latest_price is not None and sma200 is not None and latest_price > sma200
                    else "Price Below",
                    "score": min(
                        10.0,
                        max(
                            0.0,
                            (4.0 if latest_price is not None and sma200 is not None and latest_price > sma200 else 0.0)
                            + (2.0 if sma50 is not None and sma200 is not None and sma50 > sma200 else 0.0)
                            + (1.0 if slope_direction == "Up" else 0.0),
                        ),
                    ),
                    "regime": trend_context["direction"],
                }
        if include("ema_20"):
            if ema20 is None or sma50 is None or latest_price is None:
                indicators["ema_20"] = {
                    "value": ema20,
                    "signal": "Insufficient data",
                    "score": None,
                    "regime": "Insufficient data",
                }
            else:
                indicators["ema_20"] = {
                    "value": ema20,
                    "signal": "Price Above"
                    if latest_price is not None and ema20 is not None and latest_price > ema20
                    else "Price Below",
                    "score": min(
                        10.0,
                        max(
                            0.0,
                            (2.0 if latest_price is not None and ema20 is not None and latest_price > ema20 else 0.0)
                            + (2.0 if ema20 is not None and sma50 is not None and ema20 > sma50 else 0.0)
                            + (1.0 if slope_direction == "Up" else 0.0),
                        ),
                    ),
                    "regime": trend_context["direction"],
                }

        if include("rsi"):
            indicators["rsi"] = self._rsi_signal(rsi_latest, trend_context["direction"])
        if include("macd"):
            indicators["macd"] = self._macd_signal()
        if include("stoch"):
            indicators["stoch"] = self._stoch_signal()
        if include("obv"):
            indicators["obv"] = self._obv_trend(price_series)
        if include("volume_spike"):
            indicators["volume_spike"] = self._volume_spike(price_series)
        if include("atr"):
            indicators["atr"] = self._atr_regime(latest_price)
        if include("bbands"):
            indicators["bbands"] = self._bbands_signal(latest_price)

        trend_items = [indicators[k] for k in ["sma_50", "sma_200", "ema_20"] if k in indicators]
        momentum_items = [indicators[k] for k in ["rsi", "macd", "stoch"] if k in indicators]
        volume_items = [indicators[k] for k in ["obv", "volume_spike"] if k in indicators]
        volatility_items = [indicators[k] for k in ["atr", "bbands"] if k in indicators]

        trend_score = self._avg_score(trend_items)
        momentum_score = self._avg_score(momentum_items)
        volume_score = self._avg_score(volume_items)
        volatility_score = self._avg_score(volatility_items)

        category_scores = {
            "trend_score": trend_score,
            "momentum_score": momentum_score,
            "volume_score": volume_score,
            "volatility_score": volatility_score,
        }

        overall = 0.0
        weight_sum = 0.0
        weights = {"trend_score": 0.35, "momentum_score": 0.30, "volume_score": 0.20, "volatility_score": 0.15}
        for key, weight in weights.items():
            score = category_scores.get(key)
            if score is not None:
                overall += score * weight
                weight_sum += weight
        overall_technical_score = (overall / weight_sum) if weight_sum else None

        entry_signal = "Neutral"
        exit_signal = "Neutral"
        if overall_technical_score is not None:
            if overall_technical_score >= 7.5:
                entry_signal = "Strong Bullish"
            elif overall_technical_score >= 6.0:
                entry_signal = "Bullish"
            elif overall_technical_score < 4.0:
                exit_signal = "Bearish"

        volatility_level = indicators["atr"].get("signal")
        if momentum_score is None:
            momentum_strength = "Insufficient data"
        elif momentum_score >= 8.5:
            momentum_strength = "Very Strong"
        elif momentum_score >= 7.0:
            momentum_strength = "Strong"
        elif momentum_score >= 5.0:
            momentum_strength = "Moderate"
        else:
            momentum_strength = "Weak"

        explanations = {}
        for key, item in indicators.items():
            explanations[key] = {
                "value": item.get("value"),
                "signal": item.get("signal"),
                "score": item.get("score"),
                "regime": item.get("regime"),
            }

        return {
            "latest_price": latest_price,
            "trend_direction": trend_context["direction"],
            "trend_slope": slope,
            "entry_signal": entry_signal,
            "exit_signal": exit_signal,
            "momentum_strength": momentum_strength,
            "volatility_level": volatility_level,
            "indicators": indicators,
            "category_scores": category_scores,
            "overall_technical_score": overall_technical_score,
            "explanations": explanations,
        }
