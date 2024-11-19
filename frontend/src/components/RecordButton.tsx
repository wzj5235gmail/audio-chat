import { useEffect, useRef, memo, Dispatch, useContext } from "react";
import React from "react";
import { HistoryAction } from "../reducers/historyReducer";
import { stt } from "../api/api";
import { LanguageContext } from "../contexts/LanguageContext";

interface RecordButtonProps {
  dispatch: Dispatch<HistoryAction>;
  sendMessage: (message: string) => void;
  setIsRecording: (isRecording: boolean) => void;
}

const RecordButton: React.FC<RecordButtonProps> = ({
  dispatch,
  sendMessage,
  setIsRecording
}) => {
  const recordBtnRef = useRef<HTMLButtonElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const startTime = useRef<number | null>(null);
  const endTime = useRef<number | null>(null);
  const readyRef = useRef<boolean>(false);
  const isCancelledRef = useRef<boolean>(false);
  const initialTouchYRef = useRef<number | null>(null);
  const { t } = useContext(LanguageContext);

  const handleStopRecord = async () => {
    if (readyRef.current && mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleCancelRecord = (e: React.TouchEvent) => {
    const currentTouchY = e.touches[0].clientY;
    if (initialTouchYRef.current && initialTouchYRef.current - currentTouchY > 50) {
      isCancelledRef.current = true;
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop();
      }
      alert("录音取消");
      setIsRecording(false);
    }
  };

  const getMimeType = (): string => {
    const ua = navigator.userAgent.toLowerCase();
    if (/iphone|ipad|ipod|mac/.test(ua) && !/chrome/.test(ua)) {
      return "audio/mp4";
    } else {
      return "audio/webm";
    }
  };

  useEffect(() => {
    const setupMediaRecorder = async () => {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert(
          "Your browser does not support audio recording. Please use a modern browser."
        );
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getMimeType();
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      mediaRecorderRef.current.onstop = async () => {
        if (!recordBtnRef.current) return;
        recordBtnRef.current.classList.remove("scale-90");
        recordBtnRef.current.classList.remove("bg-red-400");
        recordBtnRef.current.classList.remove("text-white");
        recordBtnRef.current.classList.add("text-red-400");
        endTime.current = Date.now();
        const recordingDuration = startTime.current ? (endTime.current - startTime.current) / 1000 : 0;
        if (recordingDuration < 0.5) {
          audioChunksRef.current = [];
          alert("录音失败：录音长度小于0.5秒");
          return;
        }
        if (isCancelledRef.current) {
          audioChunksRef.current = [];
          return;
        }
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        audioChunksRef.current = [];
        if (audioBlob.size === 0) {
          console.error("Audio blob is empty");
          return;
        }
        const audioUrl = URL.createObjectURL(audioBlob);
        dispatch({
          type: "ADD_HISTORY",
          payload: {
            time: Date.now(),
            role: "user",
            message: "...",
            audio_url: audioUrl,
            isAudio: true,
          },
        });
        const formData = new FormData();
        formData.append(
          "audio",
          audioBlob,
          mimeType === "audio/webm" ? "recording.webm" : "recording.mp4"
        );
        const transcription = await stt(audioBlob);
        if (!transcription) {
          console.error("Failed to upload audio file");
          return;
        }
        dispatch({
          type: "CHANGE_LAST_HISTORY",
          payload: {
            field: "message",
            value: transcription,
          },
        });
        sendMessage(transcription);
      };
    };

    async function setup() {
      await setupMediaRecorder();
      if (!recordBtnRef.current) return;
      recordBtnRef.current.classList.remove("border-gray-200");
      recordBtnRef.current.classList.remove("text-gray-200");
      recordBtnRef.current.classList.add("border-red-400");
      recordBtnRef.current.classList.add("text-red-400");
      readyRef.current = true;
    }
    setup();
  }, [sendMessage, dispatch]);

  const handleStartRecord = async (e: React.TouchEvent) => {
    isCancelledRef.current = false;
    initialTouchYRef.current = e.touches[0].clientY;
    if (readyRef.current && mediaRecorderRef.current) {
      mediaRecorderRef.current.start(1000);
      startTime.current = Date.now();
      if (recordBtnRef.current) {
        recordBtnRef.current.classList.add("scale-90");
        recordBtnRef.current.classList.add("bg-red-400");
        recordBtnRef.current.classList.add("text-white");
        recordBtnRef.current.classList.remove("text-red-400");
      }
      setIsRecording(true);
    }
  };

  return (
    <button
      onTouchStart={handleStartRecord}
      onTouchEnd={handleStopRecord}
      onTouchMove={handleCancelRecord}
      className="border-2 border-gray-200 text-gray-200 px-4 py-2 rounded-lg flex-grow transition no-select"
      ref={recordBtnRef}
    >
      {t("pressToTalk")}
    </button>
  );
};

export default memo(RecordButton);
