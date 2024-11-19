import React, { useEffect, useRef, memo, useContext } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import { getAudio } from "../api/api";

interface ChatMessageAudioProps {
  isUser: boolean;
  audioUrl?: string;
  loading?: boolean;
}

const ChatMessageAudio: React.FC<ChatMessageAudioProps> = ({
  isUser,
  audioUrl,
  loading,
}) => {
  const { t } = useContext(LanguageContext);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    let audioObjectUrl: string | null = null;

    const handlePlayAudio = async () => {
      try {
        if (!audioRef.current) return;

        if (audioUrl?.startsWith("/api")) {
          const blob = await getAudio(audioUrl);
          const audioBlob = new Blob([blob], { type: 'audio/mpeg' });
          audioObjectUrl = URL.createObjectURL(audioBlob);
          audioRef.current.src = audioObjectUrl;
        } else {
          audioRef.current.src = audioUrl || "";
        }

        await audioRef.current.load();
      } catch (error) {
        console.error("Error loading audio:", error);
      }
    };

    handlePlayAudio();

    return () => {
      if (audioObjectUrl) {
        URL.revokeObjectURL(audioObjectUrl);
      }
    };
  }, [audioUrl]);

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
