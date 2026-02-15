import ScoreCard from "./ScoreCard.jsx";

export default function AnalysisResult({ data }) {
  if (!data) return null;

  const combined = data.combined || {};
  const fundamental = data.fundamental || {};
  const technical = data.technical || {};

  const toneForBias = (bias) => {
    if (!bias) return "neutral";
    if (bias.toLowerCase().includes("bear")) return "bear";
    if (bias.toLowerCase().includes("bull")) return "bull";
    return "neutral";
  };

  return (
    <div className="results">
      <div className="section">
        <div className="section-title">Combined Score</div>
        <div className="grid">
          <ScoreCard title="Overall" value={combined.overall_score?.toFixed?.(2)} tone={toneForBias(combined.investment_bias)} />
          <ScoreCard title="Bias" value={combined.investment_bias || "-"} tone={toneForBias(combined.investment_bias)} />
          <ScoreCard title="Confidence" value={combined.confidence || "-"} />
        </div>
      </div>

      <div className="section">
        <div className="section-title">Fundamentals</div>
        <div className="grid">
          <ScoreCard title="Profitability" value={fundamental.category_scores?.profitability?.toFixed?.(2)} />
          <ScoreCard title="Growth" value={fundamental.category_scores?.growth?.toFixed?.(2)} />
          <ScoreCard title="Financial Strength" value={fundamental.category_scores?.financial_strength?.toFixed?.(2)} />
          <ScoreCard title="Valuation" value={fundamental.category_scores?.valuation?.toFixed?.(2)} />
        </div>
      </div>

      <div className="section">
        <div className="section-title">Technicals</div>
        <div className="grid">
          <ScoreCard title="Trend" value={technical.trend_direction || "-"} />
          <ScoreCard title="Momentum" value={technical.momentum_strength || "-"} />
          <ScoreCard title="Volatility" value={technical.volatility_level || "-"} />
          <ScoreCard title="Entry" value={technical.entry_signal || "-"} />
        </div>
      </div>
    </div>
  );
}
