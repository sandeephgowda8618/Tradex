from app.services.fundamental_engine import FundamentalEngine


def _fundamental_strong():
    return {
        "overview": {"PERatio": "18.5", "EVToEBITDA": "10.2"},
        "income_statement": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "totalRevenue": "120000", "netIncome": "18000", "operatingIncome": "22000", "ebit": "21000", "interestExpense": "500"},
                {"fiscalDateEnding": "2023-12-31", "totalRevenue": "110000", "netIncome": "16500", "operatingIncome": "20500", "ebit": "19500", "interestExpense": "600"},
                {"fiscalDateEnding": "2022-12-31", "totalRevenue": "100000", "netIncome": "15000", "operatingIncome": "19000", "ebit": "18000", "interestExpense": "700"},
                {"fiscalDateEnding": "2021-12-31", "totalRevenue": "90000", "netIncome": "13000", "operatingIncome": "17000", "ebit": "16000", "interestExpense": "800"},
            ]
        },
        "balance_sheet": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "totalShareholderEquity": "80000", "totalAssets": "150000", "totalLiabilities": "70000", "totalCurrentAssets": "50000", "totalCurrentLiabilities": "25000", "totalDebt": "20000"},
                {"fiscalDateEnding": "2023-12-31", "totalShareholderEquity": "76000", "totalAssets": "140000", "totalLiabilities": "64000", "totalCurrentAssets": "47000", "totalCurrentLiabilities": "24000", "totalDebt": "21000"},
                {"fiscalDateEnding": "2022-12-31", "totalShareholderEquity": "72000", "totalAssets": "130000", "totalLiabilities": "58000", "totalCurrentAssets": "45000", "totalCurrentLiabilities": "23000", "totalDebt": "22000"},
                {"fiscalDateEnding": "2021-12-31", "totalShareholderEquity": "68000", "totalAssets": "120000", "totalLiabilities": "52000", "totalCurrentAssets": "43000", "totalCurrentLiabilities": "22000", "totalDebt": "23000"},
            ]
        },
        "cash_flow": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "operatingCashflow": "24000", "capitalExpenditures": "-5000", "freeCashFlow": "29000"},
                {"fiscalDateEnding": "2023-12-31", "operatingCashflow": "22000", "capitalExpenditures": "-5000", "freeCashFlow": "27000"},
                {"fiscalDateEnding": "2022-12-31", "operatingCashflow": "20000", "capitalExpenditures": "-5000", "freeCashFlow": "25000"},
                {"fiscalDateEnding": "2021-12-31", "operatingCashflow": "18000", "capitalExpenditures": "-4000", "freeCashFlow": "22000"},
            ]
        },
        "earnings": {
            "annualEarnings": [
                {"fiscalDateEnding": "2024-12-31", "reportedEPS": "6.20"},
                {"fiscalDateEnding": "2023-12-31", "reportedEPS": "5.80"},
                {"fiscalDateEnding": "2022-12-31", "reportedEPS": "5.30"},
                {"fiscalDateEnding": "2021-12-31", "reportedEPS": "4.90"},
            ]
        },
    }


def _fundamental_bad():
    return {
        "overview": {"PERatio": "45.0", "EVToEBITDA": "35.0"},
        "income_statement": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "totalRevenue": "80000", "netIncome": "-5000", "operatingIncome": "-2000", "ebit": "-2500", "interestExpense": "3000"},
                {"fiscalDateEnding": "2023-12-31", "totalRevenue": "85000", "netIncome": "-3000", "operatingIncome": "-1000", "ebit": "-1500", "interestExpense": "2800"},
                {"fiscalDateEnding": "2022-12-31", "totalRevenue": "90000", "netIncome": "-1000", "operatingIncome": "500", "ebit": "300", "interestExpense": "2600"},
                {"fiscalDateEnding": "2021-12-31", "totalRevenue": "95000", "netIncome": "1000", "operatingIncome": "2000", "ebit": "1500", "interestExpense": "2400"},
            ]
        },
        "balance_sheet": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "totalShareholderEquity": "10000", "totalAssets": "120000", "totalLiabilities": "110000", "totalCurrentAssets": "15000", "totalCurrentLiabilities": "30000", "totalDebt": "70000"},
                {"fiscalDateEnding": "2023-12-31", "totalShareholderEquity": "12000", "totalAssets": "118000", "totalLiabilities": "106000", "totalCurrentAssets": "14000", "totalCurrentLiabilities": "28000", "totalDebt": "68000"},
                {"fiscalDateEnding": "2022-12-31", "totalShareholderEquity": "14000", "totalAssets": "115000", "totalLiabilities": "101000", "totalCurrentAssets": "13000", "totalCurrentLiabilities": "26000", "totalDebt": "66000"},
                {"fiscalDateEnding": "2021-12-31", "totalShareholderEquity": "16000", "totalAssets": "110000", "totalLiabilities": "94000", "totalCurrentAssets": "12000", "totalCurrentLiabilities": "24000", "totalDebt": "64000"},
            ]
        },
        "cash_flow": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "operatingCashflow": "-2000", "capitalExpenditures": "-3000", "freeCashFlow": "-5000"},
                {"fiscalDateEnding": "2023-12-31", "operatingCashflow": "-1000", "capitalExpenditures": "-2500", "freeCashFlow": "-3500"},
                {"fiscalDateEnding": "2022-12-31", "operatingCashflow": "500", "capitalExpenditures": "-2000", "freeCashFlow": "-1500"},
                {"fiscalDateEnding": "2021-12-31", "operatingCashflow": "1500", "capitalExpenditures": "-1500", "freeCashFlow": "0"},
            ]
        },
        "earnings": {
            "annualEarnings": [
                {"fiscalDateEnding": "2024-12-31", "reportedEPS": "-0.80"},
                {"fiscalDateEnding": "2023-12-31", "reportedEPS": "-0.50"},
                {"fiscalDateEnding": "2022-12-31", "reportedEPS": "-0.10"},
                {"fiscalDateEnding": "2021-12-31", "reportedEPS": "0.10"},
            ]
        },
    }


def _fundamental_neutral():
    return {
        "overview": {"PERatio": "24.0", "EVToEBITDA": "16.0"},
        "income_statement": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "totalRevenue": "100000", "netIncome": "8000", "operatingIncome": "12000", "ebit": "11000", "interestExpense": "1200"},
                {"fiscalDateEnding": "2023-12-31", "totalRevenue": "98000", "netIncome": "7600", "operatingIncome": "11500", "ebit": "10800", "interestExpense": "1150"},
                {"fiscalDateEnding": "2022-12-31", "totalRevenue": "97000", "netIncome": "7400", "operatingIncome": "11200", "ebit": "10500", "interestExpense": "1100"},
                {"fiscalDateEnding": "2021-12-31", "totalRevenue": "96000", "netIncome": "7200", "operatingIncome": "11000", "ebit": "10200", "interestExpense": "1050"},
            ]
        },
        "balance_sheet": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "totalShareholderEquity": "45000", "totalAssets": "100000", "totalLiabilities": "55000", "totalCurrentAssets": "28000", "totalCurrentLiabilities": "20000", "totalDebt": "25000"},
                {"fiscalDateEnding": "2023-12-31", "totalShareholderEquity": "44000", "totalAssets": "98000", "totalLiabilities": "54000", "totalCurrentAssets": "27500", "totalCurrentLiabilities": "19500", "totalDebt": "24500"},
                {"fiscalDateEnding": "2022-12-31", "totalShareholderEquity": "43000", "totalAssets": "96000", "totalLiabilities": "53000", "totalCurrentAssets": "27000", "totalCurrentLiabilities": "19000", "totalDebt": "24000"},
                {"fiscalDateEnding": "2021-12-31", "totalShareholderEquity": "42000", "totalAssets": "94000", "totalLiabilities": "52000", "totalCurrentAssets": "26500", "totalCurrentLiabilities": "18500", "totalDebt": "23500"},
            ]
        },
        "cash_flow": {
            "annualReports": [
                {"fiscalDateEnding": "2024-12-31", "operatingCashflow": "12000", "capitalExpenditures": "-4000", "freeCashFlow": "16000"},
                {"fiscalDateEnding": "2023-12-31", "operatingCashflow": "11500", "capitalExpenditures": "-3800", "freeCashFlow": "15300"},
                {"fiscalDateEnding": "2022-12-31", "operatingCashflow": "11000", "capitalExpenditures": "-3600", "freeCashFlow": "14600"},
                {"fiscalDateEnding": "2021-12-31", "operatingCashflow": "10500", "capitalExpenditures": "-3400", "freeCashFlow": "13900"},
            ]
        },
        "earnings": {
            "annualEarnings": [
                {"fiscalDateEnding": "2024-12-31", "reportedEPS": "3.20"},
                {"fiscalDateEnding": "2023-12-31", "reportedEPS": "3.10"},
                {"fiscalDateEnding": "2022-12-31", "reportedEPS": "3.00"},
                {"fiscalDateEnding": "2021-12-31", "reportedEPS": "2.90"},
            ]
        },
    }


def test_fundamental_strong_case():
    data = _fundamental_strong()
    engine = FundamentalEngine(
        overview=data["overview"],
        income_statement=data["income_statement"],
        balance_sheet=data["balance_sheet"],
        cash_flow=data["cash_flow"],
        earnings=data["earnings"],
    )
    result = engine.analyze()

    assert result["overall_score"] is not None
    assert result["overall_score"] >= 6.5
    assert result["risk"]["level"] == "Low"


def test_fundamental_bad_case():
    data = _fundamental_bad()
    engine = FundamentalEngine(
        overview=data["overview"],
        income_statement=data["income_statement"],
        balance_sheet=data["balance_sheet"],
        cash_flow=data["cash_flow"],
        earnings=data["earnings"],
    )
    result = engine.analyze()

    assert result["overall_score"] is not None
    assert result["overall_score"] < 4
    assert result["risk"]["level"] == "High"


def test_fundamental_neutral_case():
    data = _fundamental_neutral()
    engine = FundamentalEngine(
        overview=data["overview"],
        income_statement=data["income_statement"],
        balance_sheet=data["balance_sheet"],
        cash_flow=data["cash_flow"],
        earnings=data["earnings"],
    )
    result = engine.analyze()

    assert result["overall_score"] is not None
    assert 4 <= result["overall_score"] <= 6
