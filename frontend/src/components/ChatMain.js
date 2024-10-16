import { useState, useRef, useEffect, memo, useReducer } from "react";
import { historyReducer } from "../reducers/historyReducer";
import SendMsg from "./SendMsg";
import ChatHistory from "./ChatHistory";

const ChatMain = ({ currCharacter, setIsLogin, setIsDrawerOpen }) => {
  const [history, dispatch] = useReducer(historyReducer, []);
  const audioRef = useRef(new Audio());
  const [isRecording, setIsRecording] = useState(false);
  // const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    const expires_at = localStorage.getItem("token_expire_at");
    if (!token || Date.now() / 1000 > Number(expires_at)) {
      setIsLogin(false);
    }
  }, []);

  return (
    <div className="flex flex-col h-full">
      <div className="grid grid-cols-3 px-4 items-center justify-center lg:flex">
        <button
          className="px-4 py-2 border rounded-lg justify-self-start lg:hidden"
          onClick={() => setIsDrawerOpen(true)}
        >
          选择角色
        </button>
        <h1 className="text-xl font-semibold my-4 justify-self-center">
          {currCharacter.name}
        </h1>
        {/* <LogoutDropdown handleLogout={handleLogout} /> */}
      </div>
      {/* {showDropdown && (
        <div className="absolute">
          <button onClick={handleLogout} className="text-white">
            登出
          </button>
        </div>
      )} */}
      <ChatHistory {...{ history, dispatch, currCharacter }} />
      <SendMsg
        {...{ setIsRecording, audioRef, dispatch, history, currCharacter }}
      />
      {isRecording && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 no-select">
          <span className="text-white text-lg">
            正在录音...（手指上划可取消录音）
          </span>
        </div>
      )}
    </div>
  );
};

export default memo(ChatMain);
