import { memo } from "react";
import ChatListItem from "./ChatListItem";
import { FiLogOut } from "react-icons/fi";
import { useState, useEffect, useContext, useRef } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import LanguageSwitcher from "./LanguageSwitcher";
import React from "react";
import { Character } from "../interfaces/interfaces";
import { fetchCharacters } from "../api/api";
import UserOptionsDropdown from "./UserOptionsDropdown";

interface ChatListProps {
  setCurrCharacter: (character: Character) => void;
  setIsChatting: (isChatting: boolean) => void;
  setIsDrawerOpen: (isOpen: boolean) => void;
  isLogin: boolean;
  setIsLoginModalOpen: (isOpen: boolean) => void;
  handleLogout: () => void;
}

const ChatList: React.FC<ChatListProps> = ({ setCurrCharacter, setIsChatting, setIsDrawerOpen, isLogin, setIsLoginModalOpen, handleLogout }) => {
  const { t } = useContext(LanguageContext);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return;
    const tokenExpireAt = localStorage.getItem("token_expire_at");
    if (tokenExpireAt && new Date(parseInt(tokenExpireAt) * 1000) < new Date()) {
      handleLogout();
      window.location.reload();
      return;
    }
    const getCharacters = async () => {
      const characters = await fetchCharacters();
      setCharacters(characters);
    };
    getCharacters();
  }, [handleLogout]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);



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
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="text-xl rounded border px-4 py-2 bg-white hover:bg-gray-50"
            >
              {localStorage.getItem("nickname") ? localStorage.getItem("nickname") : localStorage.getItem("username")}
            </button>
            {isDropdownOpen && (
              <UserOptionsDropdown />
            )}
          </div>
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
