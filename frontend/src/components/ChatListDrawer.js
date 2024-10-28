import { Drawer } from "flowbite-react";
import ChatList from "./ChatList";
import { useMediaQuery } from "react-responsive";


export function ChatListDrawer({
  setCurrCharacter,
  setIsChatting,
  isDrawerOpen,
  setIsDrawerOpen,
  msg,
  setMsg,
  isLogin,
  setIsLoginModalOpen,
}) {
  const handleClose = () => setIsDrawerOpen(false);
  const isLargeScreen = useMediaQuery({ query: "(min-width: 1024px)" });

  return !isLargeScreen ? (
    <Drawer
      open={isDrawerOpen}
      onClose={handleClose}
      className="w-full max-w-md p-0"
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
