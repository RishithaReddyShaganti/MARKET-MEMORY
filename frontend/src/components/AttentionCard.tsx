import type { AttentionItem } from "../services/api";

type Props = {
  item: AttentionItem;
  onClick: () => void;
};

const companyNames: Record<string, string> = {
  TATAMOTORS: "Tata Motors",
  INFY: "Infosys",
  RELIANCE: "Reliance",
  HDFCBANK: "HDFC Bank",
  "M&M": "M&M",
  MARUTI: "Maruti",
};

function company(symbol: string) {
  return companyNames[symbol] ?? symbol;
}

function AttentionCard({ item, onClick }: Props) {
  const levelClass = item.attention_level.toLowerCase().replace(" ", "-");
  const explanation = item.explanation?.replace(/; deterministic attention score.*\.$/, ".")
    ?? "Meaningful market activity was detected.";

  return (
    <button type="button" className={`attention-card ${levelClass}`} onClick={onClick}>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="text-lg font-semibold">{company(item.symbol)}</h3>
          <span className="text-xs text-slate-500">{item.symbol}</span>
        </div>
        <p className="mt-2 text-sm text-slate-400">
          Significance {item.significance.toFixed(0)}
          <span className="mx-2 text-slate-700">·</span>
          Relevance {item.relevance.toFixed(0)}
        </p>
        <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-300">{explanation}</p>
        <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-400">
          Trace the change <span>→</span>
        </span>
      </div>
      <div className="card-score">
        <strong>{item.attention_score.toFixed(0)}</strong>
        <span>/100</span>
      </div>
    </button>
  );
}

export default AttentionCard;
