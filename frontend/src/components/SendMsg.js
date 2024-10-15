import { useState, memo } from "react";
import RecordButton from "./RecordButton";
import {
  gptModelPaths,
  referPaths,
  referTexts,
  sovitsModelPaths,
} from "../configs/configs";

const SendMsg = ({
  audioRef,
  setHistory,
  setIsRecording,
  dispatch,
  history,
  currCharacter,
}) => {
  const [message, setMessage] = useState("");
  const [sendVoice, setSendVoice] = useState(false);

  const sendMessage = async (voiceMessage) => {
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
      alert("不能发送空信息");
      dispatch({
        type: "DELETE_LAST_HISTORY",
      });
    } else {
      const chatResponse = await fetch(
        `${process.env.REACT_APP_HOST}/api/chat/${currCharacter.id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            content: typeof voiceMessage === "string" ? voiceMessage : message,
          }),
        }
      );

      let result = "";

      if (chatResponse.ok) {
        const data = await chatResponse.json();
        result = data.message;
        const translation = data.translation;
        // console.log("translation:", data.translation);
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
      const id = currCharacter.id;
      const resultToAudio = result.replace(/[\r|\n|\\s]+/g, "");
      const audioResponse = await fetch(
        // `${process.env.REACT_APP_GENERATE_AUDIO_HOST}/api/generate_audio`,
        `http://localhost:9880/api/generate_audio`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            text: resultToAudio,
            text_language: "日文",
            gpt_path: gptModelPaths[id],
            sovits_path: sovitsModelPaths[id],
            refer_wav_path: referPaths[id],
            prompt_text: referTexts[id],
            prompt_language: "日文",
          }),
        }
      );

      if (audioResponse.ok) {
        const blob = await audioResponse.blob();
        const url = window.URL.createObjectURL(blob);
        // 设置audioUrl
        dispatch({
          type: "CHANGE_LAST_HISTORY",
          payload: {
            field: "audioUrl",
            value: url,
          },
        });
        // 取消loading状态
        dispatch({
          type: "CHANGE_LAST_HISTORY",
          payload: {
            field: "loading",
            value: false,
          },
        });
        // 播放audio
        audioRef.current.src = url;
        audioRef.current.play();
      } else {
        alert("Failed to generate audio");
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
          <RecordButton {...{ setHistory, sendMessage, setIsRecording }} />
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
            rows="1"
            placeholder="请输入..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                sendMessage();
              }
            }}
          ></input>
          <button
            id="send"
            onClick={sendMessage}
            className="px-4 py-2 rounded-lg border-2 border-red-400 text-red-400"
          >
            发送
          </button>
        </div>
      )}
    </div>
  );
};

export default memo(SendMsg);
