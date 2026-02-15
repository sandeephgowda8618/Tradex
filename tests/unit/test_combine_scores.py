from app.services.analysis_orchestrator import AnalysisOrchestrator


def test_combine_scores_both():
    orchestrator = AnalysisOrchestrator(alpha_service=None)
    result = orchestrator._combine_scores(
        {"overall_score": 8.0},
        {"overall_technical_score": 6.0},
    )
    assert result["overall_score"] == 7.2
    assert result["investment_bias"] in {"Bullish", "Strong Bullish"}


def test_combine_scores_fundamental_only():
    orchestrator = AnalysisOrchestrator(alpha_service=None)
    result = orchestrator._combine_scores({"overall_score": 6.5}, None)
    assert result["overall_score"] == 6.5


def test_combine_scores_technical_only():
    orchestrator = AnalysisOrchestrator(alpha_service=None)
    result = orchestrator._combine_scores(None, {"overall_technical_score": 5.5})
    assert result["overall_score"] == 5.5


def test_combine_scores_none():
    orchestrator = AnalysisOrchestrator(alpha_service=None)
    result = orchestrator._combine_scores(None, None)
    assert result["overall_score"] is None
    assert result["confidence"] == "Low"
