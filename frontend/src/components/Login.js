import { useState, memo, useContext } from "react";
import { LanguageContext } from "../contexts/LanguageContext";
import LanguageSwitcher from "./LanguageSwitcher";

const Login = ({ setIsLogin }) => {
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [registerForm, setRegisterForm] = useState({
    username: "",
    password: "",
  });
  const [showRegister, setShowRegister] = useState(false);
  const { t } = useContext(LanguageContext);

  function handleLogin(e) {
    e.preventDefault();
    fetch(`/api/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `username=${loginForm.username}&password=${loginForm.password}`,
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.access_token) {
          localStorage.setItem("token", res.access_token);
          localStorage.setItem("token_expire_at", res.expires_at);
          localStorage.setItem("user_id", res.user_id);
          localStorage.setItem("username", res.username);
          setIsLogin(true);
          setLoginForm({ username: "", password: "" });
        } else {
          alert(t("loginFailed"));
        }
      })
      .catch((e) => {
        console.log(e);
        alert(t("loginFailed"));
      });
  }

  function handleTestUserLogin(e) {
    e.preventDefault();
    setLoginForm({ username: "abc@gmail.com", password: "123456" });
  }

  function handleRegister(e) {
    e.preventDefault();
    fetch(`/api/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: registerForm.username,
        password: registerForm.password,
      }),
    })
      .then((res) => res.json())
      .then((res) => {
        if (res.username) {
          alert(`${t("registerSuccess")}${res.username}`);
          setRegisterForm({ username: "", password: "" });
          setShowRegister(false);
        } else {
          alert(t("registerFailed"));
        }
      })
      .catch((e) => {
        console.log(e);
        alert(t("registerFailed"));
      });
  }

  return (
    <div className="w-screen h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
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
                  onChange={(e) =>
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
                  onChange={(e) =>
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
            <div className="flex items-center justify-center mt-2">
              <button
                className="border hover:border-blue-500 text-blue-600 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
                onClick={handleTestUserLogin}
              >
                {t("testUserLogin")}
              </button>
            </div>
          </>
        )}
        {showRegister && (
          <>
            <h2 className="text-2xl font-bold mb-6 text-center">{t("register")}</h2>
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
                  onChange={(e) =>
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
                  onChange={(e) =>
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
    </div>
  );
};

export default memo(Login);
