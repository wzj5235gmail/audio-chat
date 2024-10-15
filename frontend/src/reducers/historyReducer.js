export const historyReducer = (history, action) => {
  let newHistory = [...history];
  switch (action.type) {
    case "INIT_HISTORY":
      return action.payload;
    case "ADD_HISTORY":
      return [...history, action.payload];
    case "CHANGE_LAST_HISTORY":
      newHistory[newHistory.length - 1][action.payload.field] =
        action.payload.value;
      return newHistory;
    case "DELETE_LAST_HISTORY":
      return newHistory.slice(0, -1);
    default:
      return history;
  }
};
