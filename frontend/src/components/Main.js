import { useState, useEffect, memo } from "react";
import Login from "./Login";
import ChatMain from "./ChatMain";
import ChatListDrawer from "./ChatListDrawer";

const Main = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isChatting, setIsChatting] = useState(false);
  const [currCharacter, setCurrCharacter] = useState({});
  const [isDrawerOpen, setIsDrawerOpen] = useState(true);
  // if not token or token expired, change login state
  useEffect(() => {
    const token = localStorage.getItem("token");
    const expires_at = localStorage.getItem("token_expire_at");
    if (!token || Date.now() / 1000 > Number(expires_at)) {
      setIsLogin(false);
    }
  }, []);

  return (
    <div id="chat" className="flex" style={{ height: "100vh", width: "100vw" }}>
      {!isLogin ? (
        <Login setIsLogin={setIsLogin} />
      ) : (
        <>
          <ChatListDrawer
            {...{
              setCurrCharacter,
              setIsChatting,
              isDrawerOpen,
              setIsDrawerOpen,
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
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <button
                  className="text-xl font-bold py-2 px-4 rounded-full bg-red-500 hover:bg-red-600 text-white"
                  onClick={() => setIsDrawerOpen(true)}
                >
                  选择一个角色开始聊天
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default memo(Main);
