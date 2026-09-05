import type { IntentType, Watchlist, WatchlistItem } from "../types/watchlist";

export interface AttentionItem { id: string; symbol: string; significance: number; relevance: number; attention_score: number; attention_level: string; confidence: number; explanation: string | null; freshness: string | null; evidence_available: boolean; watchlist_item_id: string | null; }
export interface AttentionFeed { watched_stocks: number; events_detected: number; normal: number; worth_knowing: number; need_attention: number; items: AttentionItem[]; }
export interface EvidenceItem { id: string; type: string; description: string; source: string; reference: string | null; observed_at: string | null; freshness: string | null; verification: string | null; }
export interface TraceData { observed_facts: { symbol: string; signals: Record<string, number> }; detected_signal: { significance: number }; relevant_evidence: Array<{ description: string; verification: string }>; user_intent: string | null; generated_explanation: string | null; }

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type ItemInput = { symbol: string; company_name: string; intent_type: IntentType; intent_text?: string };

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Unable to complete the request.");
  }
  return response.status === 204 ? (undefined as T) : (response.json() as Promise<T>);
}

export const api = {
  seedDemo: () => request<{ watchlist_id: string }>("/demo/flagship", { method: "POST" }),
  attention: () => request<AttentionFeed>("/attention"),
  stockDetail: (symbol: string) => request<Record<string, unknown>>(`/stocks/${symbol}`),
  trace: (id: string) => request<TraceData>(`/insights/${id}/trace`),
  evidence: (id: string) => request<EvidenceItem[]>(`/insights/${id}/evidence`),
  listWatchlists: () => request<Watchlist[]>("/watchlists"),
  createWatchlist: (name: string) => request<Watchlist>("/watchlists", { method: "POST", body: JSON.stringify({ name }) }),
  renameWatchlist: (id: string, name: string) => request<Watchlist>(`/watchlists/${id}`, { method: "PATCH", body: JSON.stringify({ name }) }),
  deleteWatchlist: (id: string) => request<void>(`/watchlists/${id}`, { method: "DELETE" }),
  listItems: (watchlistId: string) => request<WatchlistItem[]>(`/watchlists/${watchlistId}/items`),
  addItem: (watchlistId: string, item: ItemInput) => request<WatchlistItem>(`/watchlists/${watchlistId}/items`, { method: "POST", body: JSON.stringify(item) }),
  updateItem: (watchlistId: string, itemId: string, input: Pick<ItemInput, "intent_type" | "intent_text">) => request<WatchlistItem>(`/watchlists/${watchlistId}/items/${itemId}`, { method: "PATCH", body: JSON.stringify(input) }),
  deleteItem: (watchlistId: string, itemId: string) => request<void>(`/watchlists/${watchlistId}/items/${itemId}`, { method: "DELETE" }),
};
