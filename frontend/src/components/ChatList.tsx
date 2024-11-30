import { memo } from "react";
import ChatListItem from "./ChatListItem";
import { FiLogOut } from "react-icons/fi";
import { useState, useEffect, useContext } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import LanguageSwitcher from "./LanguageSwitcher";
import React from "react";
import { Character } from "../interfaces/interfaces";
import { fetchCharacters } from "../api/api";

interface ChatListProps {
  setCurrCharacter: (character: Character) => void;
  setIsChatting: (isChatting: boolean) => void;
  setIsDrawerOpen: (isOpen: boolean) => void;
  isLogin: boolean;
  setIsLoginModalOpen: (isOpen: boolean) => void;
}

const ChatList: React.FC<ChatListProps> = ({ setCurrCharacter, setIsChatting, setIsDrawerOpen, isLogin, setIsLoginModalOpen }) => {
  const { t } = useContext(LanguageContext);
  const [characters, setCharacters] = useState<Character[]>([]);


  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    const getCharacters = async () => {
      const characters = await fetchCharacters();
      setCharacters(characters);
    };
    getCharacters();
  }, []);

  const handleLogout = (): void => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expire_at");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    localStorage.removeItem("nickname");
    window.location.reload();
  };

  return (
    <div className="flex flex-col lg:min-w-[400px]">
      <header className="bg-red-500 text-white py-4 grid grid-cols-12 items-center sticky top-0 z-10">
        <div className="col-span-3"></div>
        <h1 className="text-xl font-bold text-center col-span-6">{t("contacts")}</h1>
        <LanguageSwitcher />
      </header>
      <div className="overflow-y-auto flex-1">
        {characters.map((character) => (
          <ChatListItem
            key={character.id}
            character={character}
            setCurrCharacter={setCurrCharacter}
            setIsChatting={setIsChatting}
            setIsDrawerOpen={setIsDrawerOpen}
          />
        ))}
      </div>
      <div className="sticky bottom-0 p-4 border-t border-r flex justify-between items-center bg-white">
        {isLogin && (
          <button className="text-xl rounded border px-4 py-2 bg-white">
            {localStorage.getItem("nickname") ? localStorage.getItem("nickname") : localStorage.getItem("username")}
          </button>
        )}
        {isLogin ? (
          <button
            className="text-xl font-bold py-2 px-4 rounded bg-red-500 hover:bg-red-600 text-white"
            onClick={handleLogout}
          >
            <FiLogOut />
          </button>
        ) : (
          <button
            className="text-xl font-bold py-2 px-4 rounded bg-red-500 hover:bg-red-600 text-white"
            onClick={() => setIsLoginModalOpen(true)}
          >
            {t("login")}
          </button>
        )}
      </div>
    </div>
  );
};

export default memo(ChatList);
