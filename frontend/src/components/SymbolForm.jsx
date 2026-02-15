import { useState } from "react";

const FUNDAMENTALS = [
  "roe",
  "roa",
  "net_margin",
  "operating_margin",
  "revenue_cagr_3y",
  "eps_cagr_3y",
  "fcf_cagr_3y",
  "debt_to_equity",
  "current_ratio",
  "interest_coverage",
  "pe_ratio",
  "ev_to_ebitda",
];

const TECHNICALS = [
  "sma_50",
  "sma_200",
  "ema_20",
  "rsi",
  "macd",
  "stoch",
  "obv",
  "volume_spike",
  "atr",
  "bbands",
];

export default function SymbolForm({ onSubmit }) {
  const [symbol, setSymbol] = useState("");
  const [fundamentals, setFundamentals] = useState([]);
  const [technicals, setTechnicals] = useState([]);
  const maxFundamentals = 5;
  const maxTechnicals = 5;

  const toggle = (value, list, setList) => {
    if (list.includes(value)) {
      setList(list.filter((v) => v !== value));
      return;
    }
    setList([...list, value]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = symbol.trim().toUpperCase();
    if (!trimmed) return;
    onSubmit(trimmed, fundamentals, technicals);
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-row">
        <label className="label">Symbol</label>
        <input
          className="input"
          placeholder="AAPL"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value)}
        />
        <button className="btn" type="submit">
          Analyze
        </button>
      </div>

      <div className="form-section">
        <div className="section-title">Fundamentals</div>
        <div className="chip-grid">
          {FUNDAMENTALS.map((f) => (
            <button
              type="button"
              key={f}
              className={`chip ${fundamentals.includes(f) ? "chip-active" : ""} ${
                !fundamentals.includes(f) && fundamentals.length >= maxFundamentals ? "chip-disabled" : ""
              }`}
              onClick={() => toggle(f, fundamentals, setFundamentals)}
              disabled={!fundamentals.includes(f) && fundamentals.length >= maxFundamentals}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="hint">
          Selected {fundamentals.length} / {maxFundamentals}
        </div>
      </div>

      <div className="form-section">
        <div className="section-title">Technicals</div>
        <div className="chip-grid">
          {TECHNICALS.map((t) => (
            <button
              type="button"
              key={t}
              className={`chip ${technicals.includes(t) ? "chip-active" : ""} ${
                !technicals.includes(t) && technicals.length >= maxTechnicals ? "chip-disabled" : ""
              }`}
              onClick={() => toggle(t, technicals, setTechnicals)}
              disabled={!technicals.includes(t) && technicals.length >= maxTechnicals}
            >
              {t}
            </button>
          ))}
        </div>
        <div className="hint">
          Selected {technicals.length} / {maxTechnicals}
        </div>
      </div>
    </form>
  );
}
