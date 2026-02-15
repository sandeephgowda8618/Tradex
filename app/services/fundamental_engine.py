from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class FundamentalEngine:
    SCORING_RANGES: Dict[str, Dict[str, Any]] = {
        "roe": {"min": -0.1, "max": 0.4, "inverse": False},
        "roa": {"min": -0.1, "max": 0.2, "inverse": False},
        "net_margin": {"min": -0.1, "max": 0.4, "inverse": False},
        "operating_margin": {"min": -0.1, "max": 0.4, "inverse": False},
        "revenue_cagr_3y": {"min": -0.2, "max": 0.5, "inverse": False},
        "eps_cagr_3y": {"min": -0.2, "max": 0.5, "inverse": False},
        "fcf_cagr_3y": {"min": -0.2, "max": 0.5, "inverse": False},
        "debt_to_equity": {"min": 0.0, "max": 3.0, "inverse": True},
        "current_ratio": {"min": 0.0, "max": 3.0, "inverse": False},
        "interest_coverage": {"min": 0.0, "max": 10.0, "inverse": False},
        "pe_ratio": {"min": 5.0, "max": 40.0, "inverse": True},
        "ev_to_ebitda": {"min": 4.0, "max": 30.0, "inverse": True},
    }

    METRIC_INFO: Dict[str, Dict[str, str]] = {
        "roe": {
            "formula": "Net Income / Shareholder Equity",
            "meaning": "How efficiently equity generates profit.",
            "ideal_range": "0.15 to 0.30+",
        },
        "roa": {
            "formula": "Net Income / Total Assets",
            "meaning": "How efficiently assets generate profit.",
            "ideal_range": "0.05 to 0.15+",
        },
        "net_margin": {
            "formula": "Net Income / Revenue",
            "meaning": "Profit kept per dollar of revenue.",
            "ideal_range": "0.10 to 0.30+",
        },
        "operating_margin": {
            "formula": "Operating Income / Revenue",
            "meaning": "Operating profitability before non-operating items.",
            "ideal_range": "0.10 to 0.25+",
        },
        "revenue_cagr_3y": {
            "formula": "((Latest / Oldest) ** (1/3)) - 1",
            "meaning": "3-year compounded revenue growth rate.",
            "ideal_range": "0.05 to 0.20+",
        },
        "eps_cagr_3y": {
            "formula": "((Latest / Oldest) ** (1/3)) - 1",
            "meaning": "3-year compounded EPS growth rate.",
            "ideal_range": "0.05 to 0.25+",
        },
        "fcf_cagr_3y": {
            "formula": "((Latest / Oldest) ** (1/3)) - 1",
            "meaning": "3-year compounded free cash flow growth rate.",
            "ideal_range": "0.05 to 0.25+",
        },
        "debt_to_equity": {
            "formula": "Total Debt / Shareholder Equity",
            "meaning": "Leverage level relative to equity.",
            "ideal_range": "0.0 to 1.5",
        },
        "current_ratio": {
            "formula": "Current Assets / Current Liabilities",
            "meaning": "Short-term liquidity coverage.",
            "ideal_range": "1.2 to 2.5",
        },
        "interest_coverage": {
            "formula": "EBIT / Interest Expense",
            "meaning": "Ability to service interest from operations.",
            "ideal_range": "3.0+",
        },
        "pe_ratio": {
            "formula": "Price / Earnings",
            "meaning": "Valuation relative to earnings.",
            "ideal_range": "10 to 25",
        },
        "ev_to_ebitda": {
            "formula": "Enterprise Value / EBITDA",
            "meaning": "Valuation relative to operating cash earnings.",
            "ideal_range": "6 to 16",
        },
    }

    def __init__(
        self,
        overview: Dict[str, Any],
        income_statement: Dict[str, Any],
        balance_sheet: Dict[str, Any],
        cash_flow: Dict[str, Any],
        earnings: Dict[str, Any],
    ) -> None:
        self.overview = overview or {}
        self.income_statement = income_statement or {}
        self.balance_sheet = balance_sheet or {}
        self.cash_flow = cash_flow or {}
        self.earnings = earnings or {}

        self.years: List[int] = []
        self.revenue_series: List[Optional[float]] = []
        self.net_income_series: List[Optional[float]] = []
        self.operating_income_series: List[Optional[float]] = []
        self.ebit_series: List[Optional[float]] = []
        self.interest_expense_series: List[Optional[float]] = []
        self.equity_series: List[Optional[float]] = []
        self.assets_series: List[Optional[float]] = []
        self.liabilities_series: List[Optional[float]] = []
        self.current_assets_series: List[Optional[float]] = []
        self.current_liabilities_series: List[Optional[float]] = []
        self.debt_series: List[Optional[float]] = []
        self.operating_cashflow_series: List[Optional[float]] = []
        self.capex_series: List[Optional[float]] = []
        self.fcf_series: List[Optional[float]] = []
        self.eps_series: List[Optional[float]] = []

        self.metrics: Dict[str, Dict[str, Any]] = {}

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

    def _sort_annual_reports(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def key_fn(item: Dict[str, Any]) -> str:
            return str(item.get("fiscalDateEnding", "0000-00-00"))

        return sorted(reports, key=key_fn, reverse=True)

    def _extract_series(
        self,
        reports: List[Dict[str, Any]],
        field: str,
        limit: int = 4,
    ) -> Tuple[List[int], List[Optional[float]]]:
        sorted_reports = self._sort_annual_reports(reports)
        years: List[int] = []
        values: List[Optional[float]] = []

        for item in sorted_reports[:limit]:
            date_str = str(item.get("fiscalDateEnding", "0000-00-00"))
            year = int(date_str.split("-")[0]) if date_str else 0
            years.append(year)
            values.append(self._to_float(item.get(field)))

        return years, values

    def _extract_raw_data(self) -> None:
        income_reports = self.income_statement.get("annualReports", []) or []
        balance_reports = self.balance_sheet.get("annualReports", []) or []
        cash_reports = self.cash_flow.get("annualReports", []) or []
        earnings_reports = self.earnings.get("annualEarnings", []) or []

        self.years, self.revenue_series = self._extract_series(income_reports, "totalRevenue")
        _, self.net_income_series = self._extract_series(income_reports, "netIncome")
        _, self.operating_income_series = self._extract_series(income_reports, "operatingIncome")
        _, self.ebit_series = self._extract_series(income_reports, "ebit")
        _, self.interest_expense_series = self._extract_series(income_reports, "interestExpense")

        _, self.equity_series = self._extract_series(balance_reports, "totalShareholderEquity")
        _, self.assets_series = self._extract_series(balance_reports, "totalAssets")
        _, self.liabilities_series = self._extract_series(balance_reports, "totalLiabilities")
        _, self.current_assets_series = self._extract_series(balance_reports, "totalCurrentAssets")
        _, self.current_liabilities_series = self._extract_series(balance_reports, "totalCurrentLiabilities")
        _, self.debt_series = self._extract_series(balance_reports, "totalDebt")

        _, self.operating_cashflow_series = self._extract_series(cash_reports, "operatingCashflow")
        _, self.capex_series = self._extract_series(cash_reports, "capitalExpenditures")
        _, self.fcf_series = self._extract_series(cash_reports, "freeCashFlow")

        _, self.eps_series = self._extract_series(earnings_reports, "reportedEPS")

        if not any(self.fcf_series):
            self.fcf_series = []
            for ocf, capex in zip(self.operating_cashflow_series, self.capex_series):
                if ocf is None or capex is None:
                    self.fcf_series.append(None)
                else:
                    self.fcf_series.append(ocf - capex)

    def _safe_divide(self, numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        if numerator is None or denominator is None:
            return None
        if denominator == 0:
            return None
        return numerator / denominator

    def _cagr(self, latest: Optional[float], oldest: Optional[float], years: int = 3) -> Optional[float]:
        if latest is None or oldest is None:
            return None
        if latest <= 0 or oldest <= 0:
            return None
        if oldest == 0:
            return None
        try:
            return (latest / oldest) ** (1 / years) - 1
        except (ZeroDivisionError, ValueError):
            return None

    def _trend_stats(self, series: List[Optional[float]]) -> Dict[str, Any]:
        values = [v for v in series if v is not None]
        if len(values) < 2:
            return {
                "stdev": None,
                "positive_streak": 0,
                "stability_bonus": 0.0,
                "volatility_penalty": 0.0,
                "trend_direction": "Stable",
            }

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        stdev = variance ** 0.5

        # Series is stored as newest -> oldest. A positive streak means each year is higher than the prior year.
        positive_streak = 0
        for i in range(len(values) - 1):
            if values[i] > values[i + 1]:
                positive_streak += 1
            else:
                break

        stability_bonus = 0.5 if positive_streak >= 3 else 0.0
        volatility_penalty = 0.5 if mean != 0 and (stdev / abs(mean)) > 0.5 else 0.0
        if values[0] > values[-1]:
            trend_direction = "Uptrend"
        elif values[0] < values[-1]:
            trend_direction = "Downtrend"
        else:
            trend_direction = "Stable"

        return {
            "stdev": stdev,
            "positive_streak": positive_streak,
            "stability_bonus": stability_bonus,
            "volatility_penalty": volatility_penalty,
            "trend_direction": trend_direction,
        }

    def _score_metric(
        self,
        name: str,
        value: Optional[float],
        trend: Optional[str] = None,
        stability_bonus: float = 0.0,
        volatility_penalty: float = 0.0,
    ) -> Dict[str, Any]:
        ranges = self.SCORING_RANGES.get(name, {})
        min_val = ranges.get("min")
        max_val = ranges.get("max")
        inverse = bool(ranges.get("inverse", False))

        if value is None:
            return {"value": None, "score": None, "stability": stability_bonus, "trend": trend}

        if min_val is None or max_val is None or max_val == min_val:
            base = 0.0
        else:
            if inverse:
                base = (max_val - value) / (max_val - min_val)
            else:
                base = (value - min_val) / (max_val - min_val)
        base = max(0.0, min(1.0, base))
        score = base * 10.0
        score = max(0.0, min(10.0, score + stability_bonus - volatility_penalty))

        return {
            "value": value,
            "score": score,
            "stability": stability_bonus,
            "trend": trend,
        }

    def _compute_metrics(self, selected_metrics: Optional[List[str]] = None) -> None:
        selected = set(selected_metrics) if selected_metrics else None
        net_income = self.net_income_series[0] if self.net_income_series else None
        equity = self.equity_series[0] if self.equity_series else None
        assets = self.assets_series[0] if self.assets_series else None
        revenue = self.revenue_series[0] if self.revenue_series else None
        operating_income = self.operating_income_series[0] if self.operating_income_series else None
        ebit = self.ebit_series[0] if self.ebit_series else None
        interest = self.interest_expense_series[0] if self.interest_expense_series else None
        debt = self.debt_series[0] if self.debt_series else None
        current_assets = self.current_assets_series[0] if self.current_assets_series else None
        current_liabilities = self.current_liabilities_series[0] if self.current_liabilities_series else None

        roe = self._safe_divide(net_income, equity)
        roa = self._safe_divide(net_income, assets)
        net_margin = self._safe_divide(net_income, revenue)
        operating_margin = self._safe_divide(operating_income, revenue)

        revenue_cagr = None
        if len(self.revenue_series) >= 4:
            revenue_cagr = self._cagr(self.revenue_series[0], self.revenue_series[3], 3)

        eps_cagr = None
        if len(self.eps_series) >= 4:
            eps_cagr = self._cagr(self.eps_series[0], self.eps_series[3], 3)

        fcf_cagr = None
        if len(self.fcf_series) >= 4:
            fcf_cagr = self._cagr(self.fcf_series[0], self.fcf_series[3], 3)

        debt_to_equity = self._safe_divide(debt, equity)
        current_ratio = self._safe_divide(current_assets, current_liabilities)
        interest_coverage = self._safe_divide(ebit, interest) if interest not in {None, 0} else None

        pe_ratio = self._to_float(self.overview.get("PERatio"))
        ev_to_ebitda = self._to_float(self.overview.get("EVToEBITDA"))

        trend_rev = self._trend_stats(self.revenue_series)
        trend_eps = self._trend_stats(self.eps_series)
        trend_fcf = self._trend_stats(self.fcf_series)

        if selected is None or "roe" in selected:
            self.metrics["roe"] = self._score_metric("roe", roe, trend=None)
        if selected is None or "roa" in selected:
            self.metrics["roa"] = self._score_metric("roa", roa, trend=None)
        if selected is None or "net_margin" in selected:
            self.metrics["net_margin"] = self._score_metric("net_margin", net_margin, trend=None)
        if selected is None or "operating_margin" in selected:
            self.metrics["operating_margin"] = self._score_metric("operating_margin", operating_margin, trend=None)

        if selected is None or "revenue_cagr_3y" in selected:
            self.metrics["revenue_cagr_3y"] = self._score_metric(
                "revenue_cagr_3y",
                revenue_cagr,
                trend=trend_rev["trend_direction"],
                stability_bonus=trend_rev["stability_bonus"],
                volatility_penalty=trend_rev["volatility_penalty"],
            )
        if selected is None or "eps_cagr_3y" in selected:
            self.metrics["eps_cagr_3y"] = self._score_metric(
                "eps_cagr_3y",
                eps_cagr,
                trend=trend_eps["trend_direction"],
                stability_bonus=trend_eps["stability_bonus"],
                volatility_penalty=trend_eps["volatility_penalty"],
            )
        if selected is None or "fcf_cagr_3y" in selected:
            self.metrics["fcf_cagr_3y"] = self._score_metric(
                "fcf_cagr_3y",
                fcf_cagr,
                trend=trend_fcf["trend_direction"],
                stability_bonus=trend_fcf["stability_bonus"],
                volatility_penalty=trend_fcf["volatility_penalty"],
            )

        if selected is None or "debt_to_equity" in selected:
            self.metrics["debt_to_equity"] = self._score_metric("debt_to_equity", debt_to_equity, trend=None)
        if selected is None or "current_ratio" in selected:
            self.metrics["current_ratio"] = self._score_metric("current_ratio", current_ratio, trend=None)
        if selected is None or "interest_coverage" in selected:
            self.metrics["interest_coverage"] = self._score_metric("interest_coverage", interest_coverage, trend=None)

        if selected is None or "pe_ratio" in selected:
            if pe_ratio is None or pe_ratio <= 0:
                self.metrics["pe_ratio"] = {"value": pe_ratio, "score": None, "stability": 0.0, "trend": None}
                self.metrics["pe_ratio"]["meaningful"] = False
            else:
                self.metrics["pe_ratio"] = self._score_metric("pe_ratio", pe_ratio, trend=None)
                self.metrics["pe_ratio"]["meaningful"] = True

        if selected is None or "ev_to_ebitda" in selected:
            if ev_to_ebitda is None or ev_to_ebitda <= 0:
                self.metrics["ev_to_ebitda"] = {
                    "value": ev_to_ebitda,
                    "score": None,
                    "stability": 0.0,
                    "trend": None,
                }
                self.metrics["ev_to_ebitda"]["meaningful"] = False
            else:
                self.metrics["ev_to_ebitda"] = self._score_metric("ev_to_ebitda", ev_to_ebitda, trend=None)
                self.metrics["ev_to_ebitda"]["meaningful"] = True

    def _avg_score(self, keys: List[str]) -> Optional[float]:
        scores = [self.metrics[k]["score"] for k in keys if self.metrics.get(k, {}).get("score") is not None]
        if not scores:
            return None
        return sum(scores) / len(scores)

    def _risk_rating(self) -> Dict[str, Any]:
        flags = []
        risk_score = 0
        debt_to_equity = self.metrics.get("debt_to_equity", {}).get("value")
        if debt_to_equity is not None and debt_to_equity > 2.0:
            flags.append("high_leverage")
            risk_score += 2

        latest_fcf = self.fcf_series[0] if self.fcf_series else None
        if latest_fcf is not None and latest_fcf < 0:
            flags.append("negative_fcf")
            risk_score += 2

        if len(self.revenue_series) >= 2 and self.revenue_series[0] is not None and self.revenue_series[1] is not None:
            if self.revenue_series[0] < self.revenue_series[1]:
                flags.append("declining_revenue")
                risk_score += 1

        interest_coverage = self.metrics.get("interest_coverage", {}).get("value")
        if interest_coverage is not None and interest_coverage < 1.5:
            flags.append("weak_interest_coverage")
            risk_score += 1

        if risk_score >= 5:
            level = "High"
        elif risk_score >= 3:
            level = "Elevated"
        elif risk_score >= 1:
            level = "Moderate"
        else:
            level = "Low"

        return {"level": level, "flags": flags, "score": risk_score}

    def _quality_label(self, score: Optional[float]) -> str:
        if score is None:
            return "Insufficient data"
        if score >= 8.5:
            return "Very Strong"
        if score >= 7.0:
            return "Strong"
        if score >= 5.0:
            return "Moderate"
        if score >= 3.0:
            return "Weak"
        return "Very Weak"

    def explain_metric(self, name: str) -> Dict[str, Any]:
        meta = self.METRIC_INFO.get(name, {})
        metric = self.metrics.get(name, {})
        score = metric.get("score")
        interpretation = self._quality_label(score)
        if metric.get("meaningful") is False:
            interpretation = "Not meaningful (negative or missing)"

        return {
            "name": name,
            "formula": meta.get("formula", ""),
            "meaning": meta.get("meaning", ""),
            "ideal_range": meta.get("ideal_range", ""),
            "value": metric.get("value"),
            "score": score,
            "interpretation": interpretation,
            "trend": metric.get("trend"),
        }

    def analyze(self, selected_metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        self._extract_raw_data()
        self._compute_metrics(selected_metrics)

        category_scores = {
            "profitability": self._avg_score(["roe", "roa", "net_margin", "operating_margin"]),
            "growth": self._avg_score(["revenue_cagr_3y", "eps_cagr_3y", "fcf_cagr_3y"]),
            "financial_strength": self._avg_score(["debt_to_equity", "current_ratio", "interest_coverage"]),
            "valuation": self._avg_score(["pe_ratio", "ev_to_ebitda"]),
        }

        weighted = 0.0
        weight_sum = 0.0
        weights = {
            "profitability": 0.30,
            "growth": 0.25,
            "financial_strength": 0.25,
            "valuation": 0.20,
        }
        for key, weight in weights.items():
            if category_scores.get(key) is not None:
                weighted += category_scores[key] * weight
                weight_sum += weight

        overall_score = (weighted / weight_sum) if weight_sum > 0 else None

        explanations = {name: self.explain_metric(name) for name in self.metrics.keys()}
        business_quality_index = self._avg_score(["roe", "net_margin", "revenue_cagr_3y"])

        return {
            "raw_series": {
                "years": self.years,
                "revenue": self.revenue_series,
                "net_income": self.net_income_series,
                "operating_income": self.operating_income_series,
                "ebit": self.ebit_series,
                "interest_expense": self.interest_expense_series,
                "equity": self.equity_series,
                "assets": self.assets_series,
                "liabilities": self.liabilities_series,
                "current_assets": self.current_assets_series,
                "current_liabilities": self.current_liabilities_series,
                "debt": self.debt_series,
                "operating_cashflow": self.operating_cashflow_series,
                "capex": self.capex_series,
                "free_cash_flow": self.fcf_series,
                "eps": self.eps_series,
            },
            "metrics": self.metrics,
            "category_scores": category_scores,
            "overall_score": overall_score,
            "risk": self._risk_rating(),
            "business_quality_index": business_quality_index,
            "explanations": explanations,
        }
