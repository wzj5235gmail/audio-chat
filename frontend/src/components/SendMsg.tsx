import React, { useState, memo, useContext, ChangeEvent, KeyboardEvent, Dispatch } from "react";
import RecordButton from "./RecordButton";
import { LanguageContext } from "../contexts/LanguageContext";
import { Character } from "../interfaces/interfaces";
import { HistoryAction } from "../reducers/historyReducer";

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

  const sendMessage = async (voiceMessage?: string) => {
    if (!isLogin) {
      setIsLoginModalOpen(true);
      return;
    }
    if (sendVoice && typeof voiceMessage === "string") {
      if (voiceMessage.trim() !== "") {
        if (history.length > 0) {
          dispatch({
            type: "CHANGE_LAST_HISTORY",
            payload: {
              field: "message",
              value: voiceMessage,
            },
          });
        } else {
          dispatch({
            type: "ADD_HISTORY",
            payload: {
              time: Date.now(),
              role: "user",
              message: voiceMessage,
              isAudio: true,
            },
          });
        }
      }
    } else {
      if (message.trim() !== "") {
        dispatch({
          type: "ADD_HISTORY",
          payload: {
            time: Date.now(),
            role: "user",
            message: message,
            isAudio: false,
          },
        });
        setMessage("");
      }
    }

    const msgToSend = typeof voiceMessage === "string" ? voiceMessage : message;
    if (msgToSend.trim() === "") {
      alert(t("emptyMessage"));
      dispatch({
        type: "DELETE_LAST_HISTORY",
      });
    } else {
      const chatResponse = await fetch(
        `/api/chat/${currCharacter.id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            content: typeof voiceMessage === "string" ? voiceMessage : message,
            language: language,
          }),
        }
      );

      let result = "";

      if (chatResponse.ok) {
        const data = await chatResponse.json();
        result = data.message;
        const translation = data.translation;
        dispatch({
          type: "ADD_HISTORY",
          payload: {
            time: Date.now(),
            role: "megumi",
            message: result,
            isAudio: true,
            translation,
            loading: true,
          },
        });
      }
      const resultToAudio = result.replace(/[\r|\n|\\s]+/g, "");
      const audioResponse = await fetch(
        `/voice_generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            text: resultToAudio,
            text_language: "日文",
            gpt_path: currCharacter.gpt_model_path,
            sovits_path: currCharacter.sovits_model_path,
            refer_wav_path: currCharacter.refer_path,
            prompt_text: currCharacter.refer_text,
            prompt_language: "日文",
          }),
        }
      );

      if (audioResponse.ok) {
        const blob = await audioResponse.blob();
        const url = window.URL.createObjectURL(blob);
        dispatch({
          type: "CHANGE_LAST_HISTORY",
          payload: {
            field: "audioUrl",
            value: url,
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
          audioRef.current.src = url;
          audioRef.current.play();
        }
      } else {
        alert(t("failedToGenerateAudio"));
      }
    }
  };

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
                sendMessage();
              }
            }}
          />
          <button
            id="send"
            onClick={() => sendMessage()}
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
