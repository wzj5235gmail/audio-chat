import React, { useState, memo, useContext, ChangeEvent, KeyboardEvent, Dispatch } from "react";
import RecordButton from "./RecordButton";
import { LanguageContext } from "../contexts/LanguageContext";
import { Character } from "../interfaces/interfaces";
import { HistoryAction } from "../reducers/historyReducer";
import { generateVoice, saveAudio, sendChatMessage } from "../api/api";

interface HistoryItem {
  time: number;
  role: string;
  message: string;
  isAudio?: boolean;
  translation?: string;
  loading?: boolean;
  audioUrl?: string;
}

interface SendMsgProps {
  audioRef: React.RefObject<HTMLAudioElement>;
  setIsRecording: (isRecording: boolean) => void;
  dispatch: Dispatch<HistoryAction>;
  history: HistoryItem[];
  currCharacter: Character;
  isLogin: boolean;
  setIsLoginModalOpen: (isOpen: boolean) => void;
}

const SendMsg: React.FC<SendMsgProps> = ({
  audioRef,
  setIsRecording,
  dispatch,
  history,
  currCharacter,
  isLogin,
  setIsLoginModalOpen,
}) => {
  const [message, setMessage] = useState<string>("");
  const [sendVoice, setSendVoice] = useState<boolean>(false);
  const { t } = useContext(LanguageContext);
  const { language } = useContext(LanguageContext);


  const sendMessage = async (message: string) => {
    if (!isLogin) {
      setIsLoginModalOpen(true);
      return;
    }
    if (message.trim() === "") {
      alert(t("emptyMessage"));
      return;
    }
    setMessage("");
    const chatResponse = await sendChatMessage(currCharacter.id, message, language);
    if (!chatResponse) {
      alert(t("failedToSendMessage"));
      return;
    }
    const responseMsg = chatResponse.message;
    const conversationId = chatResponse.id;
    const translation = chatResponse.translation;
    dispatch({
      type: "ADD_HISTORY",
      payload: {
        time: Date.now(),
        role: "character",
        message: responseMsg,
        isAudio: true,
        translation,
        loading: true,
      },
    });
    const resultToAudio = responseMsg.replace(/[\r|\n|\\s]+/g, "");
    const audioResponse = await generateVoice(
      resultToAudio,
      "日文",
      currCharacter.gpt_model_path,
      currCharacter.sovits_model_path,
      currCharacter.refer_path,
      currCharacter.refer_text,
      "日文"
    );
    if (!audioResponse) {
      alert(t("failedToGenerateAudio"));
      return;
    }
    const audioUrlResponse = await saveAudio(audioResponse, conversationId);
    if (!audioUrlResponse) {
      alert(t("failedToGenerateAudio"));
      return;
    }
    const audioUrl = audioUrlResponse.audio_url;
    dispatch({
      type: "CHANGE_LAST_HISTORY",
      payload: {
        field: "audioUrl",
        value: audioUrl,
      },
    });
    dispatch({
      type: "CHANGE_LAST_HISTORY",
      payload: {
        field: "loading",
        value: false,
      },
    });
    if (audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
    }
  }

  return (
    <div className="send-msg my-4 mx-2 flex gap-4 items-center">
      {sendVoice ? (
        <div className="flex gap-4 w-full">
          <button onClick={() => setSendVoice(false)} className="border-0">
            <img
              src="keyboard-icon.png"
              alt=""
              className="object-contain"
              height={40}
              width={40}
            />
          </button>
          <RecordButton {...{ dispatch, sendMessage, setIsRecording }} />
        </div>
      ) : (
        <div className="send-text flex w-full space-between gap-4">
          <button onClick={() => setSendVoice(true)} className="border-0">
            <img
              src="audio-chat.png"
              alt=""
              className="object-contain"
              height={40}
              width={40}
            />
          </button>
          <input
            type="text"
            className=" p-2 border border-gray rounded-lg flex-grow"
            id="message"
            placeholder={t("enterMessage")}
            value={message}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)}
            onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
              if (e.key === "Enter") {
                sendMessage(message);
              }
            }}
          />
          <button
            id="send"
            onClick={() => sendMessage(message)}
            className="px-4 py-2 rounded-lg border-2 border-red-400 text-red-400"
          >
            {t("send")}
          </button>
        </div>
      )}
    </div>
  );
};

export default memo(SendMsg);
