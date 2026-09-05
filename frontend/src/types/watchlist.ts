export type IntentType =
  | "earnings"
  | "growth"
  | "valuation"
  | "competition"
  | "corporate_event"
  | "long_term_business"
  | "exploring"
  | "custom";

export interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface WatchlistItem {
  id: string;
  watchlist_id: string;
  symbol: string;
  company_name: string;
  intent_type: IntentType;
  intent_text: string | null;
  added_at: string;
  last_checked_at: string | null;
}

export const intentLabels: Record<IntentType, string> = {
  earnings: "Earnings",
  growth: "Growth",
  valuation: "Valuation",
  competition: "Competition",
  corporate_event: "Corporate Event",
  long_term_business: "Long-term Business",
  exploring: "Just Exploring",
  custom: "Custom",
};
