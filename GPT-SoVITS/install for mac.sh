#!/bin/bash

sudo true

set -e

os="$(uname)"
os_version=$(sw_vers -productVersion)
architecture=$(uname -m)
rosetta_running=$(sysctl -in sysctl.proc_translated)
required_version="14.0"

version_ge() {
  local major1="${1%%.*}"
  local major2="${2%%.*}"
  [[ "$major1" -ge "$major2" ]]
}

if [[ "${os}" == "Darwin" ]]
then
    :
else
    echo "Well, it's for Mac"
    exit 1
fi

if [[ "$rosetta_running" == "1" ]]; then
    echo "The script is running under Rosetta 2. Please close Rosetta 2 to run this script natively on ARM64."
    exit 1
fi

if version_ge $os_version $required_version && [[ "$architecture" == "arm64" ]]; then
    :
else
    echo "This script requires macOS Sonoma (14.0) or later and ARM architecture."
    exit 1
fi

if [ -z "${BASH_SOURCE[0]}" ]; then
    echo "Error: BASH_SOURCE is not defined. Make sure you are running this script in a compatible Bash environment."
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

cd "$SCRIPT_DIR"

trap 'echo "An error occurred.";exit 1' ERR

if ! xcode-select -p &>/dev/null; then
    echo "安装Xcode Command Line Tools..."
    xcode-select --install
    
    # 等待安装完成
    echo "等待Xcode Command Line Tools安装完成..."
    while true; do
        sleep 20
        
        if xcode-select -p &>/dev/null; then
            echo "Xcode Command Line Tools已安装完成。"
            break
        else
            echo "正在安装中，请稍候..."
        fi
    done
fi

# 检查Homebrew是否安装
if ! command -v brew &>/dev/null; then
    echo "安装Homebrew..."
    /bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"
    source ~/.zprofile
fi

# 检查git-lfs是否安装
if ! command -v git-lfs &>/dev/null; then
    echo "安装git lfs..."
    brew install git-lfs
fi

# 检查 ffmpeg 是否已安装
if command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg 已安装."
else
    echo "ffmpeg 未安装."
    echo "安装 ffmpeg..."
    brew install ffmpeg  
fi

# 安装virtualenv
echo "安装virtualenv..."
sudo chown -R $(whoami) /opt/homebrew
if ! command -v virtualenv &>/dev/null; then
    echo "安装virtualenv..."
    brew install virtualenv
fi

sudo spctl --master-disable

sudo xattr -dr com.apple.quarantine "./runtime"

# 创建运行脚本
echo "创建启动脚本 go-webui.command..."

cat <<'EOF' >./go-webui.command
#!/bin/bash

# 检查Xcode命令行工具是否安装
if ! xcode-select -p &>/dev/null; then
    echo "安装Xcode Command Line Tools..."
    xcode-select --install
fi

# 检查Homebrew是否安装
if ! command -v brew &>/dev/null; then
    echo "安装Homebrew..."
    /bin/zsh -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"
fi

# 检查 ffmpeg 是否已安装
if command -v ffmpeg >/dev/null 2>&1; then
    echo "ffmpeg 已安装."
else
    echo "ffmpeg 未安装."
    echo "安装 ffmpeg..."
    brew install ffmpeg  
fi

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

cd "$SCRIPT_DIR"

source "./runtime/bin/activate"

echo "乐"

"./runtime/bin/python3" webui.py

EOF

chmod +x ./go-webui.command

cat <<'EOF' >./update.command
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

cd "$SCRIPT_DIR"

git pull --rebase

source "./runtime/bin/activate"

pip3 install -r "./requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EOF

chmod +x ./update.command

echo "部署完成,点击go-webui.command以打开,点击update.command以拉取更新"

rm -- "$0"