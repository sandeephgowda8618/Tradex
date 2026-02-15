import "../index.css";

export default function ScoreCard({ title, value, tone = "neutral" }) {
  return (
    <div className={`card card-${tone}`}>
      <div className="card-title">{title}</div>
      <div className="card-value">{value ?? "-"}</div>
    </div>
  );
}
