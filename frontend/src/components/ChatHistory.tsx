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
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ history, dispatch, currCharacter }) => {
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const getHistory = async (userId: string) => {
    const historyFromDB = await getConversations(parseInt(userId), currCharacter.id);
    dispatch({ type: "INIT_HISTORY", payload: historyFromDB });
  };

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) return;
    getHistory(userId);
  }, [currCharacter.id, dispatch, getHistory]);

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
            audioUrl={item.audioUrl}
            loading={item.loading}
            translation={item.translation}
            isAudio={item.isAudio}
            currCharacter={currCharacter}
          />
        ))}
    </div>
  );
};

export default memo(ChatHistory);
