import { FC } from "react";
import Modal from "./Modal";
import Login from "./Login";
import React from "react";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  setIsLogin: (isLogin: boolean) => void;
}

const LoginModal: FC<LoginModalProps> = ({ isOpen, onClose, setIsLogin }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <Login setIsLogin={setIsLogin} onClose={onClose} />
    </Modal>
  );
};

export default LoginModal;
