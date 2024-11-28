import { useState, memo, useContext, FormEvent, ChangeEvent } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import LanguageSwitcher from "./LanguageSwitcher";
import React from "react";
import { login, register } from "../api/api";

interface LoginProps {
  setIsLogin: (isLogin: boolean) => void;
  onClose: () => void;
}

interface FormState {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token?: string;
  expires_at?: string;
  user_id?: string;
  username?: string;
}

interface RegisterResponse {
  username?: string;
}

const Login = ({ setIsLogin, onClose }: LoginProps) => {
  const [loginForm, setLoginForm] = useState<FormState>({ username: "", password: "" });
  const [registerForm, setRegisterForm] = useState<FormState>({
    username: "",
    password: "",
  });
  const [showRegister, setShowRegister] = useState<boolean>(false);
  const { t } = useContext(LanguageContext);

  async function handleLogin(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data: LoginResponse = await login(loginForm.username, loginForm.password);
    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("token_expire_at", data.expires_at || "");
      localStorage.setItem("user_id", data.user_id || "");
      localStorage.setItem("username", data.username || "");
      setIsLogin(true);
      setLoginForm({ username: "", password: "" });
      onClose();
    } else {
      alert(t("loginFailed"));
    }
  }

  function handleTestUserLogin(e: FormEvent<HTMLButtonElement>) {
    e.preventDefault();
    setLoginForm({ username: "abc@gmail.com", password: "123456" });
  }

  async function handleRegister(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const res: RegisterResponse = await register(registerForm.username, registerForm.password);
    if (res.username) {
      alert(`${t("registerSuccess")}${res.username}`);
      setRegisterForm({ username: "", password: "" });
      setShowRegister(false);
    } else {
      alert(t("registerFailed"));
    }
  }

  return (
    <div>
      {!showRegister && (
        <>
          <div className="grid grid-cols-12 items-center mb-6">
            <div className="col-span-3"></div>
            <h2 className="text-2xl font-bold text-center col-span-6">{t("login")}</h2>
            <LanguageSwitcher />
          </div>
          <form onSubmit={handleLogin}>
            <div className="mb-4">
              <label
                className="block text-gray-700 text-sm font-bold mb-2 text-start"
                htmlFor="username"
              >
                {t("username")}
              </label>
              <input
                type="text"
                id="username"
                value={loginForm.username}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setLoginForm((prev) => {
                    return { ...prev, username: e.target.value };
                  })
                }
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="mb-6">
              <label
                className="block text-gray-700 text-sm font-bold mb-2 text-start"
                htmlFor="password"
              >
                {t("password")}
              </label>
              <input
                type="password"
                id="password"
                value={loginForm.password}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setLoginForm((prev) => {
                    return { ...prev, password: e.target.value };
                  })
                }
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="flex items-center justify-center">
              <button
                type="submit"
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
              >
                {t("loginButton")}
              </button>
            </div>
          </form>
          <div className="flex items-center justify-center mt-2">
            <button
              className="border hover:border-blue-500 text-blue-600 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
              onClick={() => setShowRegister(true)}
            >
              {t("goToRegister")}
            </button>
          </div>
          {/* <div className="flex items-center justify-center mt-2">
            <button
              className="border hover:border-blue-500 text-blue-600 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
              onClick={handleTestUserLogin}
            >
              {t("testUserLogin")}
            </button>
          </div> */}
        </>
      )}
      {showRegister && (
        <>
          <h2 className="text-2xl font-bold text-center mb-6">{t("register")}</h2>
          <form onSubmit={handleRegister}>
            <div className="mb-4">
              <label
                className="block text-gray-700 text-sm font-bold mb-2 text-start"
                htmlFor="username"
              >
                {t("username")}
              </label>
              <input
                type="text"
                id="username"
                value={registerForm.username}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setRegisterForm((prev) => {
                    return { ...prev, username: e.target.value };
                  })
                }
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="mb-6">
              <label
                className="block text-gray-700 text-sm font-bold mb-2 text-start"
                htmlFor="password"
              >
                {t("password")}
              </label>
              <input
                type="password"
                id="password"
                value={registerForm.password}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setRegisterForm((prev) => {
                    return { ...prev, password: e.target.value };
                  })
                }
                className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              />
            </div>
            <div className="flex items-center justify-center">
              <button
                type="submit"
                className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
              >
                {t("registerButton")}
              </button>
            </div>
            <div className="flex items-center justify-center mt-2">
              <button
                className="border hover:border-red-500 text-red-600 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
                onClick={() => setShowRegister(false)}
              >
                {t("goToLogin")}
              </button>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default memo(Login);
