import { Modal } from "flowbite-react";
import React, { useState } from "react";

const OptionButton = ({ children, onClick }: { children: React.ReactNode, onClick: () => void }) => {
  return (
    <button className="block w-full text-left px-4 py-2 text-gray-700 text-lg hover:bg-gray-100" onClick={onClick}>{children}</button>
  )
};

const ProfileSettingsModal = ({ isOpen, setIsOpen }: { isOpen: boolean, setIsOpen: React.Dispatch<React.SetStateAction<boolean>> }) => {
  return <Modal show={isOpen} onClose={() => setIsOpen(false)}>
    <div>ProfileSettingsModal</div>
  </Modal>
};

const ChangePasswordModal = ({ isOpen, setIsOpen }: { isOpen: boolean, setIsOpen: React.Dispatch<React.SetStateAction<boolean>> }) => {
  return <Modal show={isOpen} onClose={() => setIsOpen(false)}>
    <div>ChangePasswordModal</div>
  </Modal>
};

const UserOptionsDropdown = () => {
  const [isProfileSettingsModalOpen, setIsProfileSettingsModalOpen] = useState(false);
  const [isChangePasswordModalOpen, setIsChangePasswordModalOpen] = useState(false);
  return (
    <>
      <div className="absolute bottom-full mb-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
        <div className="py-1" role="menu">
          <OptionButton onClick={() => setIsProfileSettingsModalOpen(true)}>个人设置</OptionButton>
          <OptionButton onClick={() => setIsChangePasswordModalOpen(true)}>修改密码</OptionButton>
        </div>
      </div>
      <ProfileSettingsModal isOpen={isProfileSettingsModalOpen} setIsOpen={setIsProfileSettingsModalOpen} />
      <ChangePasswordModal isOpen={isChangePasswordModalOpen} setIsOpen={setIsChangePasswordModalOpen} />
    </>
  )
};

export default UserOptionsDropdown;
