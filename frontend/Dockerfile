# 开发阶段
FROM node:18-alpine AS development

# 设置安全环境变量
ENV NODE_ENV=development \
    CHOKIDAR_USEPOLLING=true \
    WATCHPACK_POLLING=true

WORKDIR /app

# 创建非root用户
RUN addgroup -g 1001 -S nodejs \
    && adduser -S nodejs -u 1001 -G nodejs

# 复制package文件
COPY package*.json ./

# 安装依赖（使用npm ci确保一致性）
RUN npm ci --only=development \
    && npm cache clean --force

# 复制源代码
COPY . .

# 设置正确的权限
RUN chown -R nodejs:nodejs /app

USER nodejs

# 开发命令（启用热重载）
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# 构建阶段
FROM node:18-alpine AS builder

# 设置构建环境变量
ENV NODE_ENV=production

WORKDIR /app

# 创建非root用户
RUN addgroup -g 1001 -S nodejs \
    && adduser -S nodejs -u 1001 -G nodejs

# 复制package文件
COPY package*.json ./

# 安装依赖（仅生产依赖）
RUN npm ci --only=production \
    && npm cache clean --force

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 设置正确的权限
RUN chown -R nodejs:nodejs /app

# 生产阶段
FROM nginx:alpine AS production

# 设置安全头部的nginx配置
COPY nginx-security.conf /etc/nginx/conf.d/security.conf
COPY nginx.conf /etc/nginx/nginx.conf

# 从构建阶段复制构建结果
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

# 移除默认的nginx配置
RUN rm /etc/nginx/conf.d/default.conf

# 创建非root用户（nginx镜像已创建nginx用户）
USER nginx

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]