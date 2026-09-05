import type { EvidenceItem } from "../services/api";

type Props = { evidence: EvidenceItem[] | null };

function EvidenceList({ evidence }: Props) {
  if (evidence === null) return <p className="mt-6 text-sm text-slate-500">Loading evidence…</p>;

  if (evidence.length === 0) {
    return <div className="empty-state mt-6"><p className="text-sm text-slate-400">No supporting evidence is available.</p></div>;
  }

  return (
    <div className="evidence-grid">
      {evidence.map((item) => (
        <article className="evidence-card" key={item.id}>
          <div className="flex items-start justify-between gap-4">
            <span className="evidence-type">{item.type.replace("_", " ")}</span>
            <span className="evidence-status">{item.verification}</span>
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-300">{item.description}</p>
          <p className="mt-5 text-xs text-slate-500">
            {item.observed_at && new Date(item.observed_at).toLocaleString()}
            {item.freshness && ` · ${item.freshness}`}
          </p>
        </article>
      ))}
    </div>
  );
}

export default EvidenceList;
