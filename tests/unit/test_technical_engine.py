from app.services.technical_engine import TechnicalEngine


def _technical_bullish():
    return {
        "daily_series": {
            "Time Series (Daily)": {
                "2025-02-14": {"4. close": "220", "2. high": "225", "3. low": "215", "5. volume": "2000000"},
                "2025-02-13": {"4. close": "218", "2. high": "222", "3. low": "214", "5. volume": "1500000"},
                "2025-02-12": {"4. close": "216", "2. high": "220", "3. low": "212", "5. volume": "1400000"},
                "2025-02-11": {"4. close": "214", "2. high": "218", "3. low": "210", "5. volume": "1350000"},
                "2025-02-10": {"4. close": "212", "2. high": "216", "3. low": "208", "5. volume": "1300000"}
            }
        },
        "rsi": {"Technical Analysis: RSI": {"2025-02-14": {"RSI": "65"}, "2025-02-13": {"RSI": "62"}}},
        "macd": {
            "Technical Analysis: MACD": {
                "2025-02-14": {"MACD": "1.5", "MACD_Signal": "1.2", "MACD_Hist": "0.3"},
                "2025-02-13": {"MACD": "1.1", "MACD_Signal": "1.2", "MACD_Hist": "-0.1"}
            }
        },
        "sma_50": {"Technical Analysis: SMA": {"2025-02-14": {"SMA": "210"}, "2025-02-13": {"SMA": "208"}}},
        "sma_200": {"Technical Analysis: SMA": {"2025-02-14": {"SMA": "190"}, "2025-02-13": {"SMA": "189"}}},
        "ema_20": {"Technical Analysis: EMA": {"2025-02-14": {"EMA": "214"}, "2025-02-13": {"EMA": "212"}}},
        "stoch": {"Technical Analysis: STOCH": {"2025-02-14": {"SlowK": "70", "SlowD": "65"}}},
        "obv": {"Technical Analysis: OBV": {"2025-02-14": {"OBV": "12000000"}, "2025-02-13": {"OBV": "11800000"}}},
        "atr": {"Technical Analysis: ATR": {"2025-02-14": {"ATR": "3.0"}, "2025-02-13": {"ATR": "2.8"}}},
        "bbands": {
            "Technical Analysis: BBANDS": {
                "2025-02-14": {"Real Upper Band": "230", "Real Lower Band": "200", "Real Middle Band": "215"},
                "2025-02-13": {"Real Upper Band": "228", "Real Lower Band": "198", "Real Middle Band": "213"}
            }
        }
    }


def _technical_bearish():
    return {
        "daily_series": {
            "Time Series (Daily)": {
                "2025-02-14": {"4. close": "120", "2. high": "125", "3. low": "115", "5. volume": "900000"},
                "2025-02-13": {"4. close": "122", "2. high": "126", "3. low": "118", "5. volume": "950000"},
                "2025-02-12": {"4. close": "124", "2. high": "128", "3. low": "120", "5. volume": "980000"},
                "2025-02-11": {"4. close": "126", "2. high": "130", "3. low": "122", "5. volume": "1000000"},
                "2025-02-10": {"4. close": "128", "2. high": "132", "3. low": "124", "5. volume": "1020000"}
            }
        },
        "rsi": {"Technical Analysis: RSI": {"2025-02-14": {"RSI": "35"}, "2025-02-13": {"RSI": "40"}}},
        "macd": {
            "Technical Analysis: MACD": {
                "2025-02-14": {"MACD": "-1.2", "MACD_Signal": "-1.0", "MACD_Hist": "-0.2"},
                "2025-02-13": {"MACD": "-0.8", "MACD_Signal": "-0.9", "MACD_Hist": "0.1"}
            }
        },
        "sma_50": {"Technical Analysis: SMA": {"2025-02-14": {"SMA": "130"}, "2025-02-13": {"SMA": "131"}}},
        "sma_200": {"Technical Analysis: SMA": {"2025-02-14": {"SMA": "150"}, "2025-02-13": {"SMA": "151"}}},
        "ema_20": {"Technical Analysis: EMA": {"2025-02-14": {"EMA": "128"}, "2025-02-13": {"EMA": "129"}}},
        "stoch": {"Technical Analysis: STOCH": {"2025-02-14": {"SlowK": "25", "SlowD": "30"}}},
        "obv": {"Technical Analysis: OBV": {"2025-02-14": {"OBV": "8000000"}, "2025-02-13": {"OBV": "8200000"}}},
        "atr": {"Technical Analysis: ATR": {"2025-02-14": {"ATR": "4.5"}, "2025-02-13": {"ATR": "4.2"}}},
        "bbands": {
            "Technical Analysis: BBANDS": {
                "2025-02-14": {"Real Upper Band": "160", "Real Lower Band": "110", "Real Middle Band": "135"},
                "2025-02-13": {"Real Upper Band": "162", "Real Lower Band": "112", "Real Middle Band": "137"}
            }
        }
    }


def _build_engine(data: dict) -> TechnicalEngine:
    return TechnicalEngine(
        daily_series=data["daily_series"],
        rsi_data=data["rsi"],
        macd_data=data["macd"],
        sma_50=data["sma_50"],
        sma_200=data["sma_200"],
        ema_20=data["ema_20"],
        stoch_data=data["stoch"],
        obv_data=data["obv"],
        atr_data=data["atr"],
        bbands_data=data["bbands"],
    )


def test_technical_bullish_case():
    data = _technical_bullish()
    engine = _build_engine(data)
    result = engine.analyze()

    assert result["overall_technical_score"] is not None
    assert result["overall_technical_score"] >= 6
    assert "Bullish" in result["entry_signal"]


def test_technical_bearish_case():
    data = _technical_bearish()
    engine = _build_engine(data)
    result = engine.analyze()

    assert result["overall_technical_score"] is not None
    assert result["overall_technical_score"] < 4
    assert result["exit_signal"] == "Bearish"
