import { type FormEvent, useState } from "react";
import { api, type AttentionFeed, type AttentionItem } from "../services/api";
import type { Watchlist, WatchlistItem } from "../types/watchlist";
import AttentionCard from "../components/AttentionCard";
import WatchlistSection from "../components/WatchlistSection";

type Props = {
  attention: AttentionFeed | null;
  watchlists: Watchlist[];
  selected: Watchlist | null;
  selectedId: string | null;
  items: WatchlistItem[];
  loading: boolean;
  error: string | null;
  onSelectWatchlist: (id: string) => void;
  onRefresh: () => Promise<void>;
  onOpenInsight: (insight: AttentionItem) => void;
  setError: (error: string | null) => void;
};

function HomePage({
  attention, watchlists, selected, selectedId, items, loading, error,
  onSelectWatchlist, onRefresh, onOpenInsight, setError,
}: Props) {
  const [watchlistName, setWatchlistName] = useState("");

  async function createWatchlist(event: FormEvent) {
    event.preventDefault();
    try {
      const list = await api.createWatchlist(watchlistName);
      setWatchlistName("");
      await onRefresh();
      onSelectWatchlist(list.id);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create watchlist.");
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="border-b border-slate-800 pb-8">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="brand-mark">MARKET MEMORY</p>
              <h1 className="mt-4 max-w-3xl text-3xl font-semibold tracking-tight sm:text-4xl">
                Don&apos;t just watch stocks.
                <br />
                <span className="text-slate-400">Understand what changed.</span>
              </h1>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
                Market Memory watches the stocks you care about and surfaces meaningful changes instead of making you scan everything.
              </p>
            </div>
            <div className="status-pill"><span className="status-dot" />Market intelligence active</div>
          </div>
        </header>

        {error && (
          <div className="mt-6 flex items-start justify-between gap-4 rounded-xl border border-rose-900 bg-rose-950/30 p-4 text-sm text-rose-200">
            <span>{error}</span>
            <button type="button" className="text-button" onClick={() => setError(null)}>×</button>
          </div>
        )}

        <section className="mt-10">
          <div className="section-heading">
            <div>
              <p className="eyebrow">WHILE YOU WERE AWAY</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                {attention ? `${attention.events_detected} meaningful ${attention.events_detected === 1 ? "change" : "changes"} detected` : "Looking for meaningful changes"}
              </h2>
            </div>
            {attention && <p className="hidden text-sm text-slate-500 sm:block">Across {attention.watched_stocks} watched {attention.watched_stocks === 1 ? "stock" : "stocks"}</p>}
          </div>

          {attention ? (
            <>
              <div className="summary-grid">
                <div className="summary-card"><span>Watched</span><strong>{attention.watched_stocks}</strong></div>
                <div className="summary-card"><span>Changes</span><strong>{attention.events_detected}</strong></div>
                <div className="summary-card attention"><span>Need attention</span><strong>{attention.need_attention}</strong></div>
                <div className="summary-card"><span>Normal / notable</span><strong>{attention.normal + attention.worth_knowing}</strong></div>
              </div>

              {attention.items.length === 0 ? (
                <div className="empty-state mt-6">
                  <p className="text-lg font-medium">Nothing meaningful changed.</p>
                  <p className="mt-2 text-sm text-slate-500">Your watchlist is quiet for now.</p>
                </div>
              ) : (
                <div className="mt-7 space-y-7">
                  {["HIGH ATTENTION", "IMPORTANT", "NOTABLE", "NORMAL"].map((level) => {
                    const group = attention.items.filter((item) => item.attention_level === level);
                    if (!group.length) return null;
                    return (
                      <div key={level}>
                        <p className="eyebrow mb-3">{level}</p>
                        <div className="space-y-3">
                          {group.map((item) => (
                            <AttentionCard key={item.id} item={item} onClick={() => onOpenInsight(item)} />
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          ) : (
            <div className="empty-state mt-6">
              <div className="loading-line" />
              <p className="mt-4 text-sm text-slate-500">Preparing your market view…</p>
            </div>
          )}
        </section>

        <section className="mt-14 border-t border-slate-800 pt-10">
          <div className="section-heading">
            <div>
              <p className="eyebrow">YOUR MARKET</p>
              <h2 className="mt-2 text-2xl font-semibold">Watchlists</h2>
            </div>
            <form className="create-watchlist" onSubmit={createWatchlist}>
              <input value={watchlistName} onChange={(event) => setWatchlistName(event.target.value)} placeholder="New watchlist" required />
              <button type="submit">Create</button>
            </form>
          </div>

          <WatchlistSection
            watchlists={watchlists}
            selected={selected}
            selectedId={selectedId}
            items={items}
            loading={loading}
            onSelectWatchlist={onSelectWatchlist}
            onRefresh={onRefresh}
            setError={setError}
          />
        </section>
      </div>
    </main>
  );
}

export default HomePage;
