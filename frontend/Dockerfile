# 使用官方的Node.js镜像作为基础镜像
FROM node:20.12.0

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY package.json package-lock.json ./

# 安装依赖
RUN npm install

# 复制所有文件
COPY . /app

# 暴露端口
EXPOSE 3000

# 运行应用
CMD ["npm", "start"]

