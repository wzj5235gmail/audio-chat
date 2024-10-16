import React, { useEffect, useRef, memo } from "react";

const ChatMessage = ({
  message,
  isUser,
  audioUrl,
  loading,
  translation,
  isAudio,
  currCharacter,
}) => {
  const ref = useRef(null);
  const ref2 = useRef(null);
  const audioRef = useRef(new Audio());

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

  const handlePlayAudio = () => {
    audioRef.current.src = audioUrl;
    audioRef.current.play().catch((error) => {
      alert("Error playing audio:", error);
    });
  };

  return (
    <div className="flex items-start gap-4 mb-4" ref={ref}>
      {/* <div className="avatar h-14 w-16"> */}
      <img
        src={isUser ? "user-avatar.jpg" : currCharacter.avatar_uri}
        alt=""
        className="object-cover rounded-lg h-12 w-12"
      />
      {/* </div> */}
      <div className="flex flex-col w-full" ref={ref2}>
        {isAudio && (
          <div
            className="message rounded-lg mb-2 px-4 py-2 text-start"
            style={{
              backgroundColor: isUser ? "#8785a2" : "#ffe2e2",
              color: isUser ? "#ffffff" : "#000000",
            }}
            onClick={handlePlayAudio}
          >
            {loading ? (
              <span className=" text-gray-400">对方正在说话...</span>
            ) : (
              // <img src="voice-icon.png" alt="" className="h-4 w-4" />
              <img src="soundwave.gif" alt="" className="h-10 w-10" />
            )}
          </div>
        )}
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
      </div>
    </div>
  );
};

export default memo(ChatMessage);
