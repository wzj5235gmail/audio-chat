import Modal from "./Modal";
import Login from "./Login";

const LoginModal = ({ isOpen, onClose, setIsLogin }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <Login setIsLogin={setIsLogin} onClose={onClose} />
    </Modal>
  );
};

export default LoginModal;
