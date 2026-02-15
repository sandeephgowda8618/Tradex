import { useEffect, useState } from "react";
import { createAnalysis, getAnalysis } from "./services/api.js";
import SymbolForm from "./components/SymbolForm.jsx";
import AnalysisResult from "./components/AnalysisResult.jsx";
import LLMSection from "./components/LLMSection.jsx";
import "./index.css";

export default function App() {
  const [analysisId, setAnalysisId] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (symbol, fundamentals, technicals) => {
    setError("");
    setLoading(true);
    setData(null);
    try {
      const res = await createAnalysis(symbol, fundamentals, technicals);
      setAnalysisId(res.data.analysis_id);
    } catch (err) {
      setError("Failed to start analysis.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!analysisId) return;

    const interval = setInterval(async () => {
      try {
        const res = await getAnalysis(analysisId);
        setData(res.data);
        if (res.data.llm_ready) {
          clearInterval(interval);
        }
      } catch (err) {
        setError("Failed to fetch analysis.");
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [analysisId]);

  return (
    <div className="page">
      <header className="header">
        <div className="title">Tradex Intelligence</div>
        <div className="subtitle">Deterministic analysis with LLM interpretation</div>
      </header>

      <SymbolForm onSubmit={handleSubmit} />

      {loading && <div className="status">Starting analysis...</div>}
      {error && <div className="status status-error">{error}</div>}

      <AnalysisResult data={data} />
      <LLMSection data={data} />
    </div>
  );
}
