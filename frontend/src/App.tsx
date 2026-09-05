import { useEffect, useState } from "react";
import {
  api,
  type AttentionFeed,
  type AttentionItem,
  type EvidenceItem,
  type TraceData,
} from "./services/api";
import type { Watchlist, WatchlistItem } from "./types/watchlist";
import HomePage from "./pages/HomePage";
import WhyThisMattersPage from "./pages/WhyThisMattersPage";

type StockDetail = {
  price?: number;
  freshness?: string;
  breakdown?: Record<string, number>;
};

let startingDataLoad: ReturnType<typeof api.seedDemo> | null = null;

function App() {
  const [page, setPage] = useState<"home" | "why">("home");
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [attention, setAttention] = useState<AttentionFeed | null>(null);
  const [selectedInsight, setSelectedInsight] = useState<AttentionItem | null>(null);
  const [trace, setTrace] = useState<TraceData | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[] | null>(null);
  const [stockDetail, setStockDetail] = useState<StockDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const selected = watchlists.find((watchlist) => watchlist.id === selectedId) ?? null;

  async function loadWatchlists(selectId?: string | null) {
    setLoading(true);
    try {
      const data = await api.listWatchlists();
      setWatchlists(data);

      const next = selectId === undefined ? selectedId ?? data[0]?.id ?? null : selectId;
      setSelectedId(next && data.some((list) => list.id === next) ? next : data[0]?.id ?? null);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load watchlists.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void (async () => {
      try {
        const startingData = (startingDataLoad ??= api.seedDemo());
        const result = await startingData;
        await loadWatchlists(result.watchlist_id);
        setAttention(await api.attention());
      } catch {
        setError("Unable to initialize Market Memory.");
      }
    })();
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setItems([]);
      return;
    }

    void api.listItems(selectedId).then(setItems).catch(() => setError("Unable to load stocks."));
  }, [selectedId]);

  async function openInsight(insight: AttentionItem) {
    setSelectedInsight(insight);
    setTrace(null);
    setEvidence(null);
    setStockDetail(null);

    try {
      const [detail, nextEvidence, nextTrace] = await Promise.all([
        api.stockDetail(insight.symbol),
        api.evidence(insight.id),
        api.trace(insight.id),
      ]);

      setStockDetail(detail as StockDetail);
      setEvidence(nextEvidence);
      setTrace(nextTrace);
      setPage("why");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load insight details.");
    }
  }

  return page === "why" && selectedInsight ? (
    <WhyThisMattersPage
      insight={selectedInsight}
      stockDetail={stockDetail}
      trace={trace}
      evidence={evidence}
      onBack={() => setPage("home")}
    />
  ) : (
    <HomePage
      attention={attention}
      watchlists={watchlists}
      selected={selected}
      selectedId={selectedId}
      items={items}
      loading={loading}
      error={error}
      onSelectWatchlist={setSelectedId}
      onRefresh={async () => {
        await loadWatchlists(selectedId);
        setAttention(await api.attention());
      }}
      onOpenInsight={openInsight}
      setError={setError}
    />
  );
}

export default App;
