import { useEffect, useRef, memo } from "react";

const RecordButton = ({ setHistory, sendMessage, setIsRecording }) => {
  const recordBtnRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const startTime = useRef(null);
  const endTime = useRef(null);
  const readyRef = useRef(false);
  const isCancelledRef = useRef(false);
  const initialTouchYRef = useRef(null);

  const handleStopRecord = async () => {
    if (readyRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleCancelRecord = (e) => {
    const currentTouchY = e.touches[0].clientY;
    if (initialTouchYRef.current - currentTouchY > 50) {
      isCancelledRef.current = true;
      mediaRecorderRef.current.stop();
      alert("录音取消");
      setIsRecording(false);
    }
  };

  const getMimeType = () => {
    const ua = navigator.userAgent.toLowerCase();
    if (/iphone|ipad|ipod|mac/.test(ua) && !/chrome/.test(ua)) {
      return "audio/mp4";
    } else if (/chrome/.test(ua)) {
      return "audio/webm";
    } else {
      return "audio/webm";
    }
  };

  const setupMediaRecorder = async () => {
    let voiceMessage = "";
    const mimeType = getMimeType();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      alert(
        "Your browser does not support audio recording. Please use a modern browser."
      );
      return;
    }
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new MediaRecorder(stream, { mimeType });
    mediaRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        // console.log("new audio chunk: ", event.data);
        audioChunksRef.current.push(event.data);
      }
    };
    mediaRecorderRef.current.onstop = async () => {
      recordBtnRef.current.classList.remove("scale-90");
      recordBtnRef.current.classList.remove("bg-red-400");
      recordBtnRef.current.classList.remove("text-white");
      recordBtnRef.current.classList.add("text-red-400");

      endTime.current = Date.now();
      const recordingDuration = (endTime.current - startTime.current) / 1000;
      if (recordingDuration < 0.5) {
        // console.log("录音长度小于0.5秒,清空audioChunks");
        audioChunksRef.current = [];
        // console.log("audio chunks", audioChunksRef.current);
        alert("录音失败：录音长度小于0.5秒");
        return;
      }

      if (isCancelledRef.current) {
        // console.log("取消录音，清空audioChunks");
        audioChunksRef.current = [];
        // console.log("audio chunks", audioChunksRef.current);
        return;
      }
      // console.log("录制完成时的audio chunks：", audioChunksRef.current);
      const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
      // console.log('录制完成，清空audioChunks');
      // console.log("audio chunks", audioChunksRef.current);
      audioChunksRef.current = [];
      if (audioBlob.size === 0) {
        console.error("Audio blob is empty");
        return;
      }
      const audioUrl = URL.createObjectURL(audioBlob);
      // console.log(audioUrl);
      setHistory((prevHistory) => [
        ...prevHistory,
        {
          time: Date.now(),
          role: "user",
          message: "...",
          audioUrl,
          isAudio: true,
        },
      ]);
      // 创建 FormData 对象并添加音频文件
      const formData = new FormData();
      formData.append(
        "audio",
        audioBlob,
        mimeType === "audio/webm" ? "recording.webm" : "recording.mp4"
      );
      // 发送请求到 API
      try {
        // const response = await fetch(`/api/stt`, {
        const response = await fetch(`${process.env.REACT_APP_HOST}/api/stt`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();
          voiceMessage = data.transcription;
          sendMessage(voiceMessage);
        } else {
          console.error("Failed to upload audio file");
        }
      } catch (error) {
        console.error("Error while uploading audio file:", error);
      }
    };
  };

  useEffect(() => {
    async function setup() {
      await setupMediaRecorder();
      recordBtnRef.current.classList.remove("border-gray-200");
      recordBtnRef.current.classList.remove("text-gray-200");
      recordBtnRef.current.classList.add("border-red-400");
      recordBtnRef.current.classList.add("text-red-400");
      readyRef.current = true;
    }
    setup();
  }, []);

  const handleStartRecord = async (e) => {
    isCancelledRef.current = false;
    initialTouchYRef.current = e.touches[0].clientY;
    if (readyRef.current) {
      mediaRecorderRef.current.start(1000);
      startTime.current = Date.now();
      recordBtnRef.current.classList.add("scale-90");
      recordBtnRef.current.classList.add("bg-red-400");
      recordBtnRef.current.classList.add("text-white");
      recordBtnRef.current.classList.remove("text-red-400");
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
      按住说话
    </button>
  );
};

export default memo(RecordButton);
