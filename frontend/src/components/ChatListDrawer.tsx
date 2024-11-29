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
}: ChatListDrawerProps) {
  const handleClose = (): void => setIsDrawerOpen(false);
  const isLargeScreen = useMediaQuery({ query: "(min-width: 1024px)" });

  return !isLargeScreen ? (
    <Drawer
      open={isDrawerOpen}
      onClose={handleClose}
      className="w-full max-w-md p-0"
      style={{ height: "85vh" }}
    >
      <ChatList
        {...{ setCurrCharacter, setIsChatting, setIsDrawerOpen, msg, setMsg, isLogin, setIsLoginModalOpen }}
      />
    </Drawer>
  ) : (
    <ChatList
      {...{ setCurrCharacter, setIsChatting, setIsDrawerOpen, msg, setMsg, isLogin, setIsLoginModalOpen }}
    />
  );
}

export default ChatListDrawer;
