import type { AttentionItem, EvidenceItem, TraceData } from "../services/api";
import TraceTimeline from "../components/TraceTimeline";
import EvidenceList from "../components/EvidenceList";

type StockDetail = {
  price?: number;
  freshness?: string;
  breakdown?: Record<string, number>;
};

type Props = {
  insight: AttentionItem;
  stockDetail: StockDetail | null;
  trace: TraceData | null;
  evidence: EvidenceItem[] | null;
  onBack: () => void;
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

function signalLabel(name: string) {
  const labels: Record<string, string> = {
    price: "Price movement",
    volume: "Volume anomaly",
    market: "Market divergence",
    sector: "Sector divergence",
    fundamental: "Fundamental change",
    event: "Corporate event",
    news: "Relevant news",
  };
  return labels[name] ?? name;
}

function WhyThisMattersPage({ insight, stockDetail, trace, evidence, onBack }: Props) {
  const signals = stockDetail?.breakdown ?? {};
  const scoreRows = Object.entries(signals)
    .filter(([, value]) => typeof value === "number" && value > 0)
    .map(([name, value]) => {
      const rawValue = Number(value);
      const percentage =
        rawValue <= 1 ? rawValue * 100 : rawValue;

      return {
        name,
        value: Math.min(Math.max(percentage, 0), 100),
      };
    });

  const explanation = insight.explanation?.replace(/; deterministic attention score.*\.$/, ".")
    ?? "The observed signals show unusual movement and trading activity relevant to your watch intent.";

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto max-w-5xl">
        <button type="button" className="back-button" onClick={onBack}>← Back to market</button>

        <header className="detail-header">
          <p className="brand-mark">MARKET MEMORY</p>
          <p className="eyebrow mt-10">WHY THIS MATTERS</p>

          <div className="mt-3 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="text-4xl font-semibold tracking-tight">{company(insight.symbol)}</h1>
              <p className="mt-2 text-sm text-slate-500">
                {insight.symbol}{stockDetail?.price !== undefined && ` · ₹${stockDetail.price}`}
              </p>
            </div>
            <div className="attention-score">
              <span>ATTENTION</span>
              <strong>{insight.attention_score.toFixed(0)}<small>/100</small></strong>
            </div>
          </div>
        </header>

        <section className="detail-section">
          <div className="detail-intro">
            <div>
              <p className="eyebrow">WHAT CHANGED</p>
              <h2 className="mt-2 text-xl font-semibold">Something worth looking at</h2>
            </div>
            <span className={`level-badge ${insight.attention_level.toLowerCase().replace(" ", "-")}`}>
              {insight.attention_level}
            </span>
          </div>

          <p className="mt-5 max-w-3xl text-base leading-7 text-slate-300">{explanation}</p>

          <div className="detail-metrics">
            <div><span>Significance</span><strong>{insight.significance.toFixed(0)}</strong></div>
            <div><span>Relevance to your intent</span><strong>{insight.relevance.toFixed(0)}</strong></div>
            <div><span>Confidence</span><strong>{(insight.confidence * 100).toFixed(0)}%</strong></div>
            <div><span>Freshness</span><strong>{insight.freshness ?? "Current"}</strong></div>
          </div>
        </section>

        <section className="detail-section">
          <p className="eyebrow">WHY IT WAS FLAGGED</p>
          <div className="signal-list">
            {scoreRows.map((row) => (
              <div className="signal-row" key={row.name}>
                <span>{signalLabel(row.name)}</span>
                <div className="signal-value">
                  <div className="signal-bar">
                    <div
                      style={{
                        width: `${row.value}%`,
                      }}
                    />
                  </div>
                  <strong>{Math.round(row.value)}</strong>
                </div>
              </div>
            ))}
        
          </div>
        </section>

        <section className="detail-section" id="trace">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="eyebrow">TRACE THE CHANGE</p>
              <h2 className="mt-2 text-xl font-semibold">From market movement to meaningful insight</h2>
            </div>
            <span className="text-xs text-slate-500">Evidence-linked</span>
          </div>
          {trace ? <TraceTimeline trace={trace} /> : <p className="mt-6 text-sm text-slate-500">Trace information is unavailable.</p>}
        </section>

        <section className="detail-section">
          <p className="eyebrow">EVIDENCE</p>
          <h2 className="mt-2 text-xl font-semibold">What supports this insight</h2>
          <EvidenceList evidence={evidence} />
        </section>

        <footer className="border-t border-slate-800 py-10 text-center text-xs text-slate-600">
          Market Memory · Explainable market intelligence
        </footer>
      </div>
    </main>
  );
}

export default WhyThisMattersPage;
