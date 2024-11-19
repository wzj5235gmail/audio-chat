import React, { memo } from "react";

interface ChatMessageTextProps {
  message: string;
  isUser: boolean;
  translation?: string;
}

const ChatMessageText: React.FC<ChatMessageTextProps> = ({
  message,
  isUser,
  translation,
}) => {
  return (
    <div
      className="message rounded-lg"
      style={{
        maxWidth: "70%",
        backgroundColor: isUser ? "#8785a2" : "#ffe2e2",
        color: isUser ? "#ffffff" : "#000000",
      }}
    >
      <div className="originalMsg py-2 px-4 text-start">{message}</div>
      {translation && (
        <div className="translation py-2 px-4 text-start border-t border-gray-300">
          {translation}
        </div>
      )}
    </div>
  );
};

export default memo(ChatMessageText);
