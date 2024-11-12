import { useState, useRef, useEffect, memo, useReducer, useContext } from "react";
import { HistoryItem, historyReducer } from "../reducers/historyReducer";
import SendMsg from "./SendMsg";
import ChatHistory from "./ChatHistory";
import { LanguageContext } from "../contexts/LanguageContext";
import React from "react";
import { Character } from "../interfaces/interfaces";

interface ChatMainProps {
  currCharacter: Character;
  setIsLogin: (isLogin: boolean) => void;
  setIsDrawerOpen: (isOpen: boolean) => void;
  isLogin: boolean;
  setIsLoginModalOpen: (isOpen: boolean) => void;
}

const ChatMain: React.FC<ChatMainProps> = ({ 
  currCharacter, 
  setIsLogin, 
  setIsDrawerOpen, 
  isLogin, 
  setIsLoginModalOpen 
}) => {
  const [history, dispatch] = useReducer(historyReducer, [] as HistoryItem[]);
  const audioRef = useRef<HTMLAudioElement>(new Audio());
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const { t } = useContext(LanguageContext);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const expires_at = localStorage.getItem("token_expire_at");
    if (!token || Date.now() / 1000 > Number(expires_at)) {
      setIsLogin(false);
    }
  }, [setIsLogin]);

  return (
    <div className="flex flex-col h-full">
      <div className="grid grid-cols-3 px-4 items-center justify-center lg:flex">
        <button
          className="px-4 py-2 border rounded-lg justify-self-start lg:hidden"
          onClick={() => setIsDrawerOpen(true)}
        >
          {t("selectCharacterShort")}
        </button>
        <h1 className="text-xl font-semibold my-4 justify-self-center">
          {t(currCharacter.name)}
        </h1>
      </div>
      <ChatHistory {...{ history, dispatch, currCharacter }} />
      <SendMsg
        {...{ setIsRecording, audioRef, dispatch, history, currCharacter, isLogin, setIsLoginModalOpen }}
      />
      {isRecording && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 no-select">
          <span className="text-white text-lg">
            {t("recording")}
          </span>
        </div>
      )}
    </div>
  );
};

export default memo(ChatMain);
