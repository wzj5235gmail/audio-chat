import React, { useRef, useEffect, memo } from "react";
import ChatMessage from "./ChatMessage";
import { Character } from "../interfaces/interfaces";
import { Dispatch } from 'react';
import { HistoryAction, HistoryItem } from '../reducers/historyReducer';
import { getConversations } from "../api/api";

interface ChatHistoryProps {
  history: HistoryItem[];
  dispatch: Dispatch<HistoryAction>;
  currCharacter: Character;
  handleLogout: () => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ history, dispatch, currCharacter, handleLogout }) => {
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) return;
    const tokenExpireAt = localStorage.getItem("token_expire_at");
    if (tokenExpireAt && new Date(parseInt(tokenExpireAt) * 1000) < new Date()) {
      handleLogout();
      window.location.reload();
      return;
    }
    const getHistory = async (userId: string) => {
      const historyFromDB = await getConversations(userId, currCharacter.id);
      dispatch({ type: "INIT_HISTORY", payload: historyFromDB });
    };
    getHistory(userId);
  }, [currCharacter.id, dispatch, handleLogout]);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [history]);

  return (
    <div
      id="history"
      className="p-4 overflow-y-auto w-full flex-1 bg-gray-100"
      ref={chatHistoryRef}
    >
      {history.length > 0 &&
        history.map((item) => (
          <ChatMessage
            key={item.time}
            message={item.message}
            isUser={item.role === "user"}
            loading={item.loading}
            translation={item.translation}
            currCharacter={currCharacter}
            audio={item.audio}
          />
        ))}
    </div>
  );
};

export default memo(ChatHistory);
