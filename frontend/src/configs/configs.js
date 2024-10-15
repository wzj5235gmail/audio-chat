export const gptModelPaths = {
  1: "GPT_weights/megumi20240607-e15.ckpt",
  2: "GPT_weights/eriri-e15.ckpt",
  3: "GPT_weights/utaha-e15.ckpt",
};

export const sovitsModelPaths = {
  1: "SoVITS_weights/megumi20240607_e8_s200.pth",
  2: "SoVITS_weights/eriri_e8_s248.pth",
  3: "SoVITS_weights/utaha_e8_s256.pth",
};

export const referPaths = {
  1: "refer/megumi/megumi-1.wav",
  2: "refer/eriri/eriri-2.wav",
  3: "refer/utaha/utaha-2.wav",
};

export const referTexts = {
  1: "主人公相手だって考えればいいのか",
  // 2: "それでね、今度のイベントに抱き枕を出そうと思ってるのよ",
  2: "そんなわけでさ 今ラフデザインやってるんだけど",
  // 3: "そう、分かればいいのよ分かれば それじゃ始めるわよ",
  3: "はいそれじゃあ次のシーン 最初はヒロインの方から抱きついてくる",
};

export const characters = [
  {
    name: "加藤惠",
    id: 1,
    avatarUri: "megumi-avatar.jpg",
    bgUri: "megumi-bg.png",
  },
  {
    name: "泽村英梨梨",
    id: 2,
    avatarUri: "eriri-avatar.jpg",
    bgUri: "eriri-bg.png",
  },
  {
    name: "霞之丘诗羽",
    id: 3,
    avatarUri: "utaha-avatar.jpg",
    bgUri: "utaha-bg.png",
  },
];
