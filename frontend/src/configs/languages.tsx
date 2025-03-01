interface Translations {
  [key: string]: {
    [key: string]: string;
  };
}

export const translations: Translations = {
  en: {
    login: "Login",
    register: "Register",
    username: "Username",
    password: "Password",
    loginButton: "Login",
    registerButton: "Register",
    goToRegister: "Register",
    goToLogin: "Login",
    testUserLogin: "Test User Login",
    selectCharacter: "Select a character to start chatting",
    selectCharacterShort: "Select Character",
    contacts: "Contacts",
    pressToTalk: "Press to Talk",
    send: "Send",
    enterMessage: "Enter message...",
    recording: "Recording... (Slide up to cancel)",
    speaking: "Speaking...",
    loginFailed: "Login failed",
    registerFailed: "Register failed",
    registerSuccess: "Registration successful, username: ",
    historyFailed: "Failed to get history",
    emptyMessage: "Cannot send empty message",
    加藤惠: "Katou Megumi",
    泽村英梨梨: "Sawamura Spencer Eriri",
    霞之丘诗羽: "Kasumigaoka Utaha",
    周防有希: "Suou Yuki",
    艾米利亚: "Emiria",
    雷姆: "Remu",
    鹿野千夏: "Kano Chinatsu",
    failedToGenerateAudio: "Failed to generate audio",
    noChatChancesRemaining: "No free chat chances remaining!",
  },
  zh: {
    login: "登录",
    register: "注册",
    username: "用户名",
    password: "密码",
    loginButton: "登录",
    registerButton: "注册",
    goToRegister: "去注册",
    goToLogin: "去登录",
    testUserLogin: "测试用户登录",
    selectCharacter: "选择一个角色开始聊天",
    selectCharacterShort: "选择角色",
    contacts: "联系人",
    pressToTalk: "按住说话",
    send: "发送",
    enterMessage: "请输入...",
    recording: "正在录音...(手指上划可取消录音)",
    speaking: "对方正在说话...",
    loginFailed: "登录失败",
    registerFailed: "注册失败",
    registerSuccess: "注册成功，用户名：",
    historyFailed: "获取历史记录失败",
    emptyMessage: "不能发送空信息",
    加藤惠: "加藤惠",
    泽村英梨梨: "泽村·斯宾塞·英梨梨",
    霞之丘诗羽: "霞之丘诗羽",
    周防有希: "周防有希",
    艾米利亚: "艾蜜莉亚",
    雷姆: "雷姆",
    鹿野千夏: "鹿野千夏",
    failedToGenerateAudio: "生成音频失败",
    noChatChancesRemaining: "免费对话次数已用完",
  }
};