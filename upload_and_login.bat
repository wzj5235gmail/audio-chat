@REM 定义ip地址变量
set IP=54.177.147.104

@REM 定义ssh key
set SSH_KEY="C:\Users\Administrator\Downloads\aws241017.pem"

@REM 定义本地根目录
set LOCAL_ROOT_DIR="C:\Users\Administrator\Desktop\audio-chat"

@REM 定义远程根目录
set REMOTE_ROOT_DIR=/home/ubuntu

@REM 定义远程用户名
set REMOTE_USER=ubuntu

@REM 使用scp命令上传文件
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\docker-compose-aws.yaml" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/docker-compose.yaml
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\.env" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/.env
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\mysql\init.sql" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/init.sql
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\remote-bash.sh" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/remote-bash.sh

tar -czvf audio-chat.tar.gz "%LOCAL_ROOT_DIR%\frontend\build"
@REM tar -czvf audio-chat.tar.gz frontend\build

@REM scp -i %SSH_KEY% "audio-chat.tar.gz" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/audio-chat.tar.gz
scp -i "C:\Users\Administrator\Downloads\aws241017.pem" audio-chat.tar.gz ubuntu@54.177.147.104:/home/ubuntu/audio-chat.tar.gz

@REM 使用ssh命令登录到服务器
ssh %REMOTE_USER%@%IP% -i %SSH_KEY%
ssh ubuntu@54.177.147.104 -i "C:\Users\Administrator\Downloads\aws241017.pem"