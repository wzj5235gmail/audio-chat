import { Drawer } from "flowbite-react";
import ChatList from "./ChatList";
import { useMediaQuery } from "react-responsive";
import React from "react";
import { Character } from "../interfaces/interfaces";

interface ChatListDrawerProps {
  setCurrCharacter: (character: Character) => void;
  setIsChatting: (isChatting: boolean) => void;
  isDrawerOpen: boolean;
  setIsDrawerOpen: (isOpen: boolean) => void;
  msg?: string;
  setMsg?: (msg: string) => void;
  isLogin: boolean;
  setIsLoginModalOpen: (isOpen: boolean) => void;
  handleLogout: () => void;
}

export function ChatListDrawer({
  setCurrCharacter,
  setIsChatting,
  isDrawerOpen,
  setIsDrawerOpen,
  msg,
  setMsg,
  isLogin,
  setIsLoginModalOpen,
  handleLogout
}: ChatListDrawerProps) {
  const handleClose = (): void => setIsDrawerOpen(false);
  const isLargeScreen = useMediaQuery({ query: "(min-width: 1024px)" });

  return !isLargeScreen ? (
    <Drawer
      open={isDrawerOpen}
      onClose={handleClose}
      className="w-full max-w-md p-0"
      style={{ height: window.innerWidth < 768 ? "85vh" : "100vh" }}
    >
      <ChatList
        {...{ setCurrCharacter, setIsChatting, setIsDrawerOpen, msg, setMsg, isLogin, setIsLoginModalOpen, handleLogout }}
      />
    </Drawer>
  ) : (
    <ChatList
      {...{ setCurrCharacter, setIsChatting, setIsDrawerOpen, msg, setMsg, isLogin, setIsLoginModalOpen, handleLogout }}
    />
  );
}

export default ChatListDrawer;
