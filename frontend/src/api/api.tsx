interface ChatResponse {
  message: string;
  id: number;
  translation: string;
}

const sendChatMessage = async (characterId: number, message: string, language: string): Promise<ChatResponse | null> => {
  try {
    const response = await fetch(
      `/api/chat/${characterId}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        content: message,
        language: language,
      }),
    }
    );
    if (!response.ok) {
      console.error("Failed to send chat message");
      return null;
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Failed to send chat message", error);
    return null;
  }
}

const generateVoice = async (
  text: string,
  text_language: string,
  gpt_path: string,
  sovits_path: string,
  refer_wav_path: string,
  prompt_text: string,
  prompt_language: string
) => {
  try {
    const response = await fetch(`/voice_generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        text: text,
        text_language: text_language,
        gpt_path: gpt_path,
        sovits_path: sovits_path,
        refer_wav_path: refer_wav_path,
        prompt_text: prompt_text,
        prompt_language: prompt_language,
      }),
    });
    if (!response.ok) {
      console.error("Failed to generate voice");
      return null;
    }
    return response.blob();
  } catch (error) {
    console.error("Failed to generate voice", error);
    return null;
  }
}

const saveAudio = async (audio: Blob, conversationId: number) => {
  try {
    const formData = new FormData();
    formData.append("audio", audio, "audio.wav");
    formData.append("conversation_id", conversationId.toString());
    const response = await fetch(`/api/save_audio`, {
      method: "POST",
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: formData,
    });
    if (!response.ok) {
      console.error("Failed to upload audio file");
      return null;
    }
    const data = await response.json();
    return data.audio_url;
  } catch (error) {
    console.error("Failed to save audio", error);
    return null;
  }
}


const stt = async (audio: Blob) => {
  try {
    const formData = new FormData();
    formData.append("audio", audio, "audio.wav");
    const response = await fetch(`/api/stt`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: formData,
    });
    if (!response.ok) {
      console.error("Failed to upload audio file");
      return null;
    }
    const data = await response.json();
    return data.transcription;
  } catch (error) {
    console.error("Failed to send STT", error);
    return null;
  }
}


export { sendChatMessage, generateVoice, saveAudio, stt };
