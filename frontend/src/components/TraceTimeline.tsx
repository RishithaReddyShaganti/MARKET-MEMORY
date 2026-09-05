import type { TraceData } from "../services/api";

type Props = {
  trace: TraceData;
};

function companyName(symbol: string) {
  const names: Record<string, string> = {
    TATAMOTORS: "Tata Motors",
    INFY: "Infosys",
    RELIANCE: "Reliance",
    HDFCBANK: "HDFC Bank",
    "M&M": "M&M",
    MARUTI: "Maruti",
  };

  return names[symbol] ?? symbol;
}

function TraceTimeline({ trace }: Props) {
  const symbol = trace.observed_facts.symbol;
  const company = companyName(symbol);

  const signals = trace.observed_facts.signals;

  const priceSignal = signals.price ?? 0;
  const volumeSignal = signals.volume ?? 0;
  const marketSignal = signals.market ?? 0;
  const sectorSignal = signals.sector ?? 0;

  const steps = [
    {
      title: "Something changed",
      description: `${company} showed a significant movement during the observed period.`,
    },
    {
      title: "The price move was unusual",
      description:
        priceSignal > 0
          ? `${company}'s price movement contributed significantly to the attention score.`
          : `A meaningful price movement was observed in ${company}.`,
    },
    {
      title: "Trading activity confirmed it",
      description:
        volumeSignal > 0
          ? "Trading activity was unusually high compared with the normal baseline."
          : "Trading activity was considered while evaluating the movement.",
    },
    {
      title: "It wasn't just the market",
      description:
        marketSignal > 0
          ? `${company} behaved differently from the broader market during the same period.`
          : `The broader market was considered to determine whether this was a market-wide move.`,
    },
    {
      title: "It wasn't just the sector",
      description:
        sectorSignal > 0
          ? `${company} also behaved differently from its sector peers.`
          : `Sector performance was compared with ${company}'s movement.`,
    },
  ];

  return (
    <div className="trace-container">
      {steps.map((step, index) => (
        <div className="trace-item" key={step.title}>
          <div className="trace-number">{index + 1}</div>

          <div>
            <strong>{step.title}</strong>
            <p>{step.description}</p>
          </div>
        </div>
      ))}

      {trace.relevant_evidence.map((item, index) => (
        <div
          className="trace-item"
          key={`${item.description}-${index}`}
        >
          <div className="trace-number">{6 + index}</div>

          <div>
            <strong>Supporting evidence</strong>
            <p>{item.description}</p>
          </div>
        </div>
      ))}

      <div className="trace-item final">
        <div className="trace-number">✓</div>

        <div>
          <strong>Why it matters</strong>

          <p>
            {trace.generated_explanation?.replace(
              /; deterministic attention score.*\.$/,
              "."
            ) ??
              "The combination of unusual movement, trading activity, and supporting context makes this change worth investigating."}
          </p>
        </div>
      </div>
    </div>
  );
}

export default TraceTimeline;