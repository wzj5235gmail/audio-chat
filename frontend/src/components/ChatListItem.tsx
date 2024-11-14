import { memo, useState, useEffect, useContext } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import React from "react";
import { Character } from "../interfaces/interfaces";
import { getConversations } from "../api/api";

interface ChatListItemProps {
  character: Character;
  setCurrCharacter: (character: Character) => void;
  setIsChatting: (isChatting: boolean) => void;
  setIsDrawerOpen: (isOpen: boolean) => void;
}

interface ConversationResponse {
  created_at: string;
  message: string;
}

function isToday(date: Date): boolean {
  const today = new Date();
  return date.getDate() === today.getDate();
}

const ChatListItem: React.FC<ChatListItemProps> = ({
  character,
  setCurrCharacter,
  setIsChatting,
  setIsDrawerOpen,
}) => {
  const { t } = useContext(LanguageContext);
  const [msg, setMsg] = useState<string>("");
  const [date, setDate] = useState<string>("");
  const userId = localStorage.getItem("user_id");
  
  
  useEffect(() => {
    const getLatestConversation = async (userId: string, characterId: number) => {
      const data: ConversationResponse[] = await getConversations(parseInt(userId), characterId, 1);
      if (data.length === 0) return;
      // format date
      const dateFromTs = new Date(Number(data[0].created_at));
      const month = dateFromTs.getMonth() + 1;
      const day = dateFromTs.getDate();
      const hour = dateFromTs.getHours();
      const minute = dateFromTs.getMinutes();
      setDate(isToday(dateFromTs) ? `${hour}:${minute}` : `${month}/${day}`);
      // format message
      const message = data[0].message;
      if (message.length > 15) {
        setMsg(message.substring(0, 15) + "...");
      } else {
        setMsg(message);
      }
    };
    if (!userId) return;
    getLatestConversation(userId, character.id);
  }, [character.id, userId]);

  const handleSelectCharacter = (): void => {
    setCurrCharacter(character);
    setIsChatting(true);
    setIsDrawerOpen(false);
  };

  return (
    <div
      className="flex gap-4 items-center border-b p-4 cursor-pointer hover:bg-gray-100"
      onClick={handleSelectCharacter}
    >
      <div
        className="w-16 h-16 rounded-lg bg-center bg-cover shrink-0"
        style={{ backgroundImage: `url(${character.avatar_uri})` }}></div>
      <div className="w-full">
        <div className="flex justify-between w-full">
          <div className="text-xl">{t(character.name)}</div>
          <div className="text-gray-400 text-lg">{date}</div>
        </div>
        <div className="text-left text-gray-400 text-lg">{msg}</div>
      </div>
    </div>
  );
};

export default memo(ChatListItem);
