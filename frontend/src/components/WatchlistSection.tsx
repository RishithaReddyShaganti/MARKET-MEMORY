import { type FormEvent, useState } from "react";
import { api } from "../services/api";
import { intentLabels, type IntentType, type Watchlist, type WatchlistItem } from "../types/watchlist";

type Props = {
  watchlists: Watchlist[];
  selected: Watchlist | null;
  selectedId: string | null;
  items: WatchlistItem[];
  loading: boolean;
  onSelectWatchlist: (id: string) => void;
  onRefresh: () => Promise<void>;
  setError: (error: string | null) => void;
};

function displayName(name: string, index: number) {
  return index === 0 ? "My Stocks" : name;
}

function WatchlistSection({
  watchlists, selected, selectedId, items, loading,
  onSelectWatchlist, onRefresh, setError,
}: Props) {
  const [rename, setRename] = useState("");
  const [editingItem, setEditingItem] = useState<WatchlistItem | null>(null);
  const [symbol, setSymbol] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [intentType, setIntentType] = useState<IntentType>("growth");
  const [intentText, setIntentText] = useState("");

  async function renameWatchlist(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    try {
      await api.renameWatchlist(selected.id, rename);
      setRename("");
      await onRefresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to rename watchlist.");
    }
  }

  async function deleteWatchlist() {
    if (!selected || !window.confirm("Delete this watchlist?")) return;
    try {
      await api.deleteWatchlist(selected.id);
      await onRefresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to delete watchlist.");
    }
  }

  async function addStock(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    try {
      await api.addItem(selected.id, {
        symbol,
        company_name: companyName,
        intent_type: intentType,
        intent_text: intentText || undefined,
      });
      setSymbol("");
      setCompanyName("");
      setIntentText("");
      await onRefresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to add stock.");
    }
  }

  async function saveIntent(event: FormEvent) {
    event.preventDefault();
    if (!selected || !editingItem) return;
    try {
      await api.updateItem(selected.id, editingItem.id, {
        intent_type: intentType,
        intent_text: intentText || undefined,
      });
      setEditingItem(null);
      setIntentText("");
      await onRefresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update intent.");
    }
  }

  async function removeItem(id: string) {
    if (!selected || !window.confirm("Remove this stock from the watchlist?")) return;
    try {
      await api.deleteItem(selected.id, id);
      await onRefresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to remove stock.");
    }
  }

  const selectedIndex = Math.max(watchlists.findIndex((item) => item.id === selected?.id), 0);

  return (
    <div className="watchlist-layout">
      <aside className="watchlist-sidebar">
        <p className="eyebrow">LISTS</p>
        <div className="mt-3 space-y-1">
          {loading ? (
            <p className="px-3 py-3 text-sm text-slate-500">Loading…</p>
          ) : (
            watchlists.map((list, index) => (
              <button type="button" key={list.id} className={`watchlist-button ${list.id === selectedId ? "active" : ""}`} onClick={() => onSelectWatchlist(list.id)}>
                {displayName(list.name, index)}
              </button>
            ))
          )}
        </div>
      </aside>

      <div className="watchlist-content">
        {!selected ? (
          <div className="empty-state"><p className="font-medium">Create a watchlist to begin.</p></div>
        ) : (
          <>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <h3 className="text-xl font-semibold">{displayName(selected.name, selectedIndex)}</h3>
              <button type="button" className="text-button danger" onClick={() => void deleteWatchlist()}>Delete</button>
            </div>

            <form className="rename-form" onSubmit={renameWatchlist}>
              <input value={rename} onChange={(event) => setRename(event.target.value)} placeholder="Rename watchlist" required />
              <button type="submit">Rename</button>
            </form>

            <div className="stock-management">
              <div>
                {items.length === 0 ? (
                  <div className="empty-state"><p className="text-sm text-slate-500">No stocks in this watchlist yet.</p></div>
                ) : (
                  items.map((item) => (
                    <article className="stock-row" key={item.id}>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <b>{item.company_name}</b>
                          <span className="text-xs text-slate-500">{item.symbol}</span>
                        </div>
                        <p className="mt-2 text-sm text-slate-500">
                          Watching for {intentLabels[item.intent_type]}
                          {item.intent_text && ` · "${item.intent_text}"`}
                        </p>
                      </div>
                      <div className="flex shrink-0 gap-2">
                        <button type="button" className="text-button" onClick={() => {
                          setEditingItem(item);
                          setIntentType(item.intent_type);
                          setIntentText(item.intent_text ?? "");
                        }}>Edit</button>
                        <button type="button" className="text-button danger" onClick={() => void removeItem(item.id)}>Remove</button>
                      </div>
                    </article>
                  ))
                )}
              </div>

              <form className="form-panel" onSubmit={editingItem ? saveIntent : addStock}>
                <p className="eyebrow">{editingItem ? "UPDATE WATCH INTENT" : "ADD A STOCK"}</p>

                {editingItem ? (
                  <h4 className="mt-2 text-lg font-semibold">{editingItem.company_name}</h4>
                ) : (
                  <>
                    <label>Symbol<input value={symbol} onChange={(event) => setSymbol(event.target.value)} placeholder="e.g. INFY" required /></label>
                    <label>Company name<input value={companyName} onChange={(event) => setCompanyName(event.target.value)} placeholder="e.g. Infosys" required /></label>
                  </>
                )}

                <label>
                  Why are you watching?
                  <select value={intentType} onChange={(event) => setIntentType(event.target.value as IntentType)}>
                    {(Object.keys(intentLabels) as IntentType[]).map((type) => <option value={type} key={type}>{intentLabels[type]}</option>)}
                  </select>
                </label>

                <label>
                  {intentType === "custom" ? "Tell us why you're watching this stock." : "Optional note"}
                  <textarea value={intentText} onChange={(event) => setIntentText(event.target.value)} placeholder="Add context for your watch..." required={intentType === "custom"} />
                </label>

                <div className="form-actions">
                  <button type="submit" className="primary-button">{editingItem ? "Save changes" : "Add stock"}</button>
                  {editingItem && <button type="button" className="text-button" onClick={() => { setEditingItem(null); setIntentText(""); }}>Cancel</button>}
                </div>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default WatchlistSection;
