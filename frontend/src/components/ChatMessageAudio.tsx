import React, { useEffect, useRef, memo, useContext } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import { decode } from "base64-arraybuffer";

interface ChatMessageAudioProps {
  isUser: boolean;
  audio?: string;
  loading?: boolean;
}

const ChatMessageAudio: React.FC<ChatMessageAudioProps> = ({
  isUser,
  audio,
  loading,
}) => {
  const { t } = useContext(LanguageContext);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    let audioObjectUrl: string | null = null;

    const handleLoadAudio = async () => {
      try {
        if (!audio) return;
        const audioBytes = decode(audio);
        const audioBlob = new Blob([audioBytes], { type: 'audio/mpeg' });
        audioObjectUrl = URL.createObjectURL(audioBlob);
        if (audioRef.current) {
          audioRef.current.src = audioObjectUrl;
          audioRef.current.load();
        }
      } catch (error) {
        console.error("Error loading audio:", error);
      }
    };

    handleLoadAudio();

    return () => {
      if (audioObjectUrl) {
        URL.revokeObjectURL(audioObjectUrl);
      }
    };
  }, [audio]);

  useEffect(() => {
    if (audioRef.current) {
      const audio = audioRef.current;

      audio.addEventListener('loadeddata', () => {
        console.log('Audio loaded successfully');
      });

      audio.addEventListener('error', (e) => {
        console.error('Audio loading error:', e);
      });
    }
  }, []);

  return (
    <div
      className="message rounded-lg mb-2 px-4 py-2 text-start"
      style={{
        backgroundColor: isUser ? "#8785a2" : "#ffe2e2",
        color: isUser ? "#ffffff" : "#000000",
      }}
    >
      {loading ? (
        <span className="text-gray-400">{t("speaking")}</span>
      ) : (
        <audio
          controls
          ref={audioRef}
          playsInline
          preload="metadata"
        />
      )}
    </div>
  );
};

export default memo(ChatMessageAudio);
