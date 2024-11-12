import { useState, useEffect, memo, useContext } from "react";
import ChatMain from "./ChatMain";
import ChatListDrawer from "./ChatListDrawer";
import { LanguageContext } from "../contexts/LanguageContext";
import LoginModal from "./LoginModal";
import React from "react";
import { Character } from "../interfaces/interfaces";

const Main = () => {
  const [isLogin, setIsLogin] = useState<boolean>(true);
  const [isChatting, setIsChatting] = useState<boolean>(false);
  const [currCharacter, setCurrCharacter] = useState<Character>({} as Character);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState<boolean>(false);
  const { t } = useContext(LanguageContext);

  // if not token or token expired, change login state
  useEffect(() => {
    const token = localStorage.getItem("token");
    const expires_at = localStorage.getItem("token_expire_at");
    if (!token || !expires_at || Date.now() / 1000 > Number(expires_at)) {
      setIsLogin(false);
    }
  }, []);

  useEffect(() => {
    if (!isLogin) {
      setIsLoginModalOpen(true);
    }
  }, [isLogin]);

  return (
    <div id="chat" className="flex" style={{ height: "100vh", width: "100vw" }}>
      <ChatListDrawer
        {...{
          setCurrCharacter,
          setIsChatting,
          isDrawerOpen,
          setIsDrawerOpen,
          isLogin,
          setIsLoginModalOpen,
        }}
      />
      <div className="w-full">
        {isChatting ? (
          <ChatMain
            {...{
              currCharacter,
              setIsLogin,
              setIsChatting,
              setIsDrawerOpen,
              isLogin,
              setIsLoginModalOpen,
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <button
              className="text-xl font-bold py-2 px-4 rounded-full bg-red-500 hover:bg-red-600 text-white"
              onClick={() => setIsDrawerOpen(true)}
            >
              {t("selectCharacter")}
            </button>
          </div>
        )}
      </div>
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        setIsLogin={setIsLogin}
      />
    </div>
  );
};

export default memo(Main);
