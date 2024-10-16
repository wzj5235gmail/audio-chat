import { memo } from "react";
import ChatListItem from "./ChatListItem";
import { FiLogOut } from "react-icons/fi";
import { useState, useEffect } from "react";

const ChatList = ({ setCurrCharacter, setIsChatting, setIsDrawerOpen }) => {
  const [characters, setCharacters] = useState([]);

  useEffect(() => {
    fetch(`${process.env.REACT_APP_HOST}/api/characters`)
      .then((response) => response.json())
      .then((data) => setCharacters(data));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("token_expire_at");
    localStorage.removeItem("user_id");
    localStorage.removeItem("username");
    window.location.reload();
  };

  return (
    <div className="flex flex-col h-full lg:min-w-[400px]">
      <header className="bg-red-500 text-white p-4 flex justify-center items-center">
        <h1 className="text-xl font-bold text-center">联系人</h1>
      </header>{" "}
      <div className="flex-grow overflow-y-auto h-full">
        {characters.map((character) => (
          <ChatListItem
            key={characters.id}
            character={character}
            setCurrCharacter={setCurrCharacter}
            setIsChatting={setIsChatting}
            setIsDrawerOpen={setIsDrawerOpen}
          />
        ))}
      </div>
      <div className="relative bottom-0 p-4 border-t border-r flex justify-between items-center">
        <button className="text-xl rounded border px-4 py-2 bg-white">
          {localStorage.getItem("username")}
        </button>
        <button
          className="text-xl font-bold py-2 px-4 rounded bg-red-500 hover:bg-red-600 text-white"
          onClick={handleLogout}
        >
          <FiLogOut />
        </button>
      </div>
    </div>
  );
};

export default memo(ChatList);
