@REM 定义ip地址变量
set IP=45.77.77.35

@REM 定义ssh key
set SSH_KEY="C:\Users\Administrator\.ssh\id_ed25519"

@REM 定义本地根目录
set LOCAL_ROOT_DIR="C:\Users\Administrator\Desktop\audio-chat"

@REM 定义远程根目录
set REMOTE_ROOT_DIR=/root

@REM 定义远程用户名
set REMOTE_USER=root

@REM 使用scp命令上传文件
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\docker-compose.yaml" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/docker-compose.yaml
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\backend\.env.backend" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/.env.backend
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\frontend\.env.frontend" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/.env.frontend
scp -i %SSH_KEY% "%LOCAL_ROOT_DIR%\mysql-init-scripts\init.sql" %REMOTE_USER%@%IP%:%REMOTE_ROOT_DIR%/init.sql

@REM 使用ssh命令登录到服务器
ssh %REMOTE_USER%@%IP% -i %SSH_KEY%