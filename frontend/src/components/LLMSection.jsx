export default function LLMSection({ data }) {
  if (!data) return null;
  const status = data.llm_status || "pending";

  return (
    <div className="section">
      <div className="section-title">LLM Interpretation</div>
      <div className={`status ${status === "failed" ? "status-error" : ""}`}>
        LLM Status: {status}
      </div>
      <div className="llm-block">
        <div className="llm-title">Executive Summary</div>
        <div className="llm-text">{data.llm_summary || "Pending"}</div>
      </div>
      <div className="llm-grid">
        <div className="llm-block">
          <div className="llm-title">Bull Case</div>
          <div className="llm-text">{data.llm_bull_case || "Pending"}</div>
        </div>
        <div className="llm-block">
          <div className="llm-title">Bear Case</div>
          <div className="llm-text">{data.llm_bear_case || "Pending"}</div>
        </div>
      </div>
      <div className="llm-grid">
        <div className="llm-block">
          <div className="llm-title">Risk Assessment</div>
          <div className="llm-text">{data.llm_risk_assessment || "Pending"}</div>
        </div>
        <div className="llm-block">
          <div className="llm-title">Confidence</div>
          <div className="llm-text">{data.llm_confidence || "Pending"}</div>
        </div>
      </div>
    </div>
  );
}
