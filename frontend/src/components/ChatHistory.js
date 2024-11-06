import React, { useRef, useEffect, memo } from "react";
import ChatMessage from "./ChatMessage";

const ChatHistory = ({ history, dispatch, currCharacter }) => {
  const chatHistoryRef = useRef(null);

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) return;
    fetch(
      `/api/conversations?user_id=${userId}&character_id=${currCharacter.id}`
    )
      .then((res) => res.json())
      .then((data) => {
        const historyFromDB = data.map((item) => ({
          time: item.created_at,
          message: item.message,
          role: item.role,
          translation: item.translation,
        }));
        dispatch({ type: "INIT_HISTORY", payload: historyFromDB });
      })
      .catch((e) => {
        alert("获取历史记录失败");
        console.log(e);
      });
  }, [currCharacter.id, dispatch]);

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
