interface HistoryItem {
  created_at?: number;
  time: number;
  message: string;
  role: string;
  translation?: string;
  audio?: string;
  loading?: boolean;
  isAudio?: boolean;
}

type HistoryAction =
  | { type: "INIT_HISTORY"; payload: HistoryItem[] }
  | { type: "ADD_HISTORY"; payload: HistoryItem }
  | { type: "CHANGE_LAST_HISTORY"; payload: { field: keyof HistoryItem; value: string | boolean } }
  | { type: "DELETE_LAST_HISTORY" };

export const historyReducer = (history: HistoryItem[], action: HistoryAction): HistoryItem[] => {
  let newHistory = [...history];
  switch (action.type) {
    case "INIT_HISTORY":
      return action.payload;
    case "ADD_HISTORY":
      return [...history, action.payload];
    case "CHANGE_LAST_HISTORY":
      const lastItem = newHistory[newHistory.length - 1];
      (lastItem[action.payload.field] as any) = action.payload.value;
      return newHistory;
    case "DELETE_LAST_HISTORY":
      return newHistory.slice(0, -1);
    default:
      return history;
  }
};

export type { HistoryItem, HistoryAction };
