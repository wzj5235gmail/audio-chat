interface ChatResponse {
  message: string;
  id: string;
  translation: string;
}

const api_url = process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL : "";
const voice_url = process.env.REACT_APP_VOICE_URL ? process.env.REACT_APP_VOICE_URL : "";

const sendChatMessage = async (characterId: string, message: string, language: string): Promise<ChatResponse | null> => {
  try {
    const response = await fetch(
      `${api_url}/api/chat/${characterId}`,
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
    console.log(data);
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
    const response = await fetch(`${voice_url}/voice_generate`, {
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

const saveAudio = async (audio: Blob, conversationId: string) => {
  try {
    const formData = new FormData();
    formData.append("audio", audio, "audio.aac");
    formData.append("conversation_id", conversationId);
    const response = await fetch(`${api_url}/api/save_audio/${conversationId}`, {
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
    const response = await fetch(`${api_url}/api/stt`, {
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

const getConversations = async (userId: string, characterId: string, limit: number = 10) => {
  const response = await fetch(
    `${api_url}/api/conversations?user_id=${userId}&character_id=${characterId}&limit=${limit}`
  );
  const data = await response.json();
  const historyFromDB = data.map((item: any) => ({
    created_at: item.created_at,
    message: item.message,
    role: item.role,
    translation: item.translation,
    audio_url: item.audio_url,
    is_audio: item.audio_url ? true : false,
    id: item._id,
  }));
  return historyFromDB;
}

const fetchCharacters = async () => {
  const response = await fetch(`${api_url}/api/characters`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  });
  const data = await response.json();
  const characters = data.map((item: any) => ({
    id: item._id,
    name: item.name,
    avatar_uri: item.avatar_uri,
    gpt_model_path: item.gpt_model_path,
    sovits_model_path: item.sovits_model_path,
    refer_path: item.refer_path,
    refer_text: item.refer_text,
  }));
  return characters;
}

const login = async (username: string, password: string) => {
  const response = await fetch(`${api_url}/api/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `username=${username}&password=${password}`,
  });
  return response.json();
}

const register = async (username: string, password: string) => {
  const response = await fetch(`${api_url}/api/users`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username,
      password: password,
    }),
  })
  return response.json();
}


const updateConversation = async (conversationId: string, audio_url: string) => {
  const response = await fetch(`${api_url}/api/conversations/${conversationId}`, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      audio_url: audio_url,
    }),
  });
  if (!response.ok) {
    console.error("Failed to update conversation");
    return null;
  }
  return response.json();
}


const getAudio = async (audio_url: string) => {
  const response = await fetch(`${api_url}${audio_url}`);
  return response.blob();
}


export {
  sendChatMessage,
  generateVoice,
  saveAudio,
  stt,
  getConversations,
  fetchCharacters,
  login,
  register,
  updateConversation,
  getAudio,
};
