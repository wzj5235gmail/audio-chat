import React, { useEffect, useRef, memo } from "react";
import { Character } from "../interfaces/interfaces";
import ChatMessageAudio from "./ChatMessageAudio";
import ChatMessageText from "./ChatMessageText";

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  audioUrl?: string;
  loading?: boolean;
  translation?: string;
  currCharacter: Character;
}

const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isUser,
  audioUrl,
  loading,
  translation,
  currCharacter,
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const ref2 = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      if (isUser) {
        ref.current.classList.add("flex-row-reverse");
      } else {
        ref.current.classList.remove("flex-row-reverse");
      }
    }
    if (ref2.current) {
      if (isUser) {
        ref2.current.classList.add("items-end");
      } else {
        ref2.current.classList.add("items-start");
      }
    }
  }, [isUser]);


  return (
    <div className="flex items-start gap-4 mb-4" ref={ref}>
      <img
        src={isUser ? "user-avatar.jpg" : currCharacter.avatar_uri}
        alt=""
        className="object-cover rounded-lg h-12 w-12"
      />
      <div className="flex flex-col w-full" ref={ref2}>
        {!isUser && (
          <ChatMessageAudio isUser={isUser} audioUrl={audioUrl} loading={loading} />
        )}
        {isUser && (
          <ChatMessageText message={message} isUser={isUser} translation={translation} />
        )}
        {!isUser && audioUrl && (
          <ChatMessageText message={message} isUser={isUser} translation={translation} />
        )}
      </div>
    </div>
  );
};

export default memo(ChatMessage);
