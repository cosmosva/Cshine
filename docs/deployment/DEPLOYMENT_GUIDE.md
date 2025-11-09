# Cshine 生产环境部署指南

> 完整的服务器部署方案 v1.0
> 
> **目标**: 将 Cshine 后端服务部署到生产服务器，支持微信小程序正式上线

## 📋 目录

- [1. 部署架构](#1-部署架构)
- [2. 服务器选择](#2-服务器选择)
- [3. 域名与证书](#3-域名与证书)
- [4. 服务器环境配置](#4-服务器环境配置)
- [5. 数据库部署](#5-数据库部署)
- [6. 后端服务部署](#6-后端服务部署)
- [7. Nginx 配置](#7-nginx-配置)
- [8. 微信小程序配置](#8-微信小程序配置)
- [9. 监控与日志](#9-监控与日志)
- [10. 备份策略](#10-备份策略)
- [11. 更新与维护](#11-更新与维护)
- [12. 常见问题](#12-常见问题)

---

## 1. 部署架构

### 1.1 架构图

```
┌─────────────┐
│ 微信小程序  │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────┐
│    Nginx (反向代理 + SSL)       │
│    Port 80/443                  │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│    FastAPI Backend              │
│    Uvicorn: 127.0.0.1:8000     │
└──────┬──────────────────────────┘
       │
       ├──────────────┬──────────────┬───────────────┐
       ▼              ▼              ▼               ▼
  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐
  │PostgreSQL│  │阿里云OSS │  │通义听悟  │  │文件系统    │
  │数据库    │  │文件存储  │  │ASR服务   │  │/uploads    │
  └─────────┘  └──────────┘  └──────────┘  └────────────┘
```

### 1.2 核心组件

| 组件 | 作用 | 部署位置 |
|------|------|---------|
| Nginx | 反向代理、SSL终止、静态文件 | 服务器 Port 80/443 |
| FastAPI | 业务逻辑、API服务 | 服务器 Port 8000 |
| PostgreSQL | 关系型数据库 | 服务器 Port 5432 |
| 阿里云 OSS | 音频文件存储 | 云端 |
| 通义听悟 | AI 语音识别 | 云端 API |

### 1.3 资源需求

**最低配置**（适合初期）：
- CPU: 2核
- 内存: 4GB
- 硬盘: 50GB SSD
- 带宽: 3Mbps

**推荐配置**（适合生产）：
- CPU: 4核
- 内存: 8GB
- 硬盘: 100GB SSD
- 带宽: 5Mbps

---

## 2. 服务器选择

### 2.1 云服务商推荐

#### 方案 A：阿里云 ECS（推荐）
- **优点**：
  - 与阿里云 OSS、通义听悟同一生态，内网传输快
  - 华东地区数据中心，国内访问速度快
  - 完善的技术文档和支持
- **价格**：
  - 2核4GB：约 ¥100/月（新用户有优惠）
  - 4核8GB：约 ¥200/月
- **购买地址**：https://www.aliyun.com/product/ecs

#### 方案 B：腾讯云轻量服务器
- **优点**：
  - 价格便宜，性价比高
  - 操作简单，适合个人项目
- **价格**：
  - 2核4GB：约 ¥74/月
  - 4核8GB：约 ¥148/月
- **购买地址**：https://cloud.tencent.com/product/lighthouse

#### 方案 C：其他选择
- **华为云**：技术实力强，价格适中
- **UCloud**：中小项目友好

### 2.2 操作系统选择

**推荐：Ubuntu 22.04 LTS 或 CentOS 7/8**

```bash
# 查看系统版本
cat /etc/os-release
```

### 2.3 购买清单

- [ ] 云服务器（ECS/轻量服务器）
- [ ] 域名（如：api.cshine.com）
- [ ] SSL 证书（推荐免费的 Let's Encrypt）
- [ ] 阿里云 OSS 存储包（按需）

---

## 3. 域名与证书

### 3.1 域名准备

#### 购买域名
- 推荐注册商：阿里云万网、腾讯云、Godaddy
- 域名建议：
  - 主域名：`cshine.com`
  - API 域名：`api.cshine.com`
  - 文件域名：`files.cshine.com`（如果不用 OSS）

#### 域名备案（必须）
**⚠️ 重要**：微信小程序要求服务器域名必须备案！

```
备案流程（约 7-20 天）：
1. 在云服务商控制台提交备案申请
2. 上传身份证、营业执照等资料
3. 等待管局审核
4. 备案通过后才能使用域名
```

#### DNS 解析配置

在域名管理后台添加 A 记录：

| 主机记录 | 记录类型 | 记录值 | TTL |
|---------|---------|--------|-----|
| @ | A | 服务器公网IP | 600 |
| api | A | 服务器公网IP | 600 |

### 3.2 SSL 证书申请

#### 方案 A：Let's Encrypt（免费，推荐）

```bash
# 安装 Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y

# 自动申请并配置证书（需要先配置好域名）
sudo certbot --nginx -d api.cshine.com

# 证书会自动配置到 Nginx，并设置自动续期
```

#### 方案 B：阿里云免费证书

1. 登录阿里云控制台
2. 进入 SSL 证书服务
3. 选择"免费证书"（20个/年）
4. 申请并下载证书
5. 手动配置到 Nginx

---

## 4. 服务器环境配置

### 4.1 连接服务器

```bash
# 使用 SSH 连接
ssh root@your_server_ip

# 首次登录建议修改密码
passwd
```

### 4.2 创建部署用户

```bash
# 创建用户（不使用 root）
sudo adduser cshine

# 添加到 sudo 组
sudo usermod -aG sudo cshine

# 切换用户
su - cshine
```

### 4.3 安装基础软件

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装必要工具
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    unzip \
    build-essential \
    software-properties-common
```

### 4.4 安装 Python 3.11

```bash
# 添加 PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# 安装 Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 安装 pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# 验证安装
python3.11 --version
pip3.11 --version
```

### 4.5 安装 Nginx

```bash
# 安装 Nginx
sudo apt install nginx -y

# 启动服务
sudo systemctl start nginx
sudo systemctl enable nginx

# 检查状态
sudo systemctl status nginx

# 测试配置
sudo nginx -t
```

### 4.6 配置防火墙

```bash
# 安装 UFW（如果没有）
sudo apt install ufw -y

# 允许 SSH、HTTP、HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status
```

---

## 5. 数据库部署

### 5.1 安装 PostgreSQL

```bash
# 安装 PostgreSQL 15
sudo apt install postgresql postgresql-contrib -y

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 检查状态
sudo systemctl status postgresql
```

### 5.2 配置数据库

```bash
# 切换到 postgres 用户
sudo -u postgres psql

# 在 PostgreSQL 交互式终端中执行：
```

```sql
-- 创建数据库
CREATE DATABASE cshine;

-- 创建用户
CREATE USER cshine_user WITH PASSWORD 'your_strong_password_here';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE cshine TO cshine_user;

-- 退出
\q
```

### 5.3 配置远程访问（可选）

如果需要本地客户端连接：

```bash
# 编辑配置文件
sudo vim /etc/postgresql/15/main/postgresql.conf

# 修改监听地址
listen_addresses = 'localhost'  # 仅本地访问（推荐）

# 编辑访问控制
sudo vim /etc/postgresql/15/main/pg_hba.conf

# 添加（仅本地）
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5

# 重启服务
sudo systemctl restart postgresql
```

### 5.4 数据库备份脚本

```bash
# 创建备份目录
sudo mkdir -p /var/backups/cshine
sudo chown cshine:cshine /var/backups/cshine

# 创建备份脚本
cat > ~/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/cshine"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="cshine_backup_$DATE.sql"

# 执行备份
PGPASSWORD='your_db_password' pg_dump -h localhost -U cshine_user cshine > "$BACKUP_DIR/$FILENAME"

# 压缩
gzip "$BACKUP_DIR/$FILENAME"

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $FILENAME.gz"
EOF

# 添加执行权限
chmod +x ~/backup_db.sh

# 添加到定时任务（每天凌晨2点）
crontab -e
# 添加这一行：
# 0 2 * * * /home/cshine/backup_db.sh >> /home/cshine/backup.log 2>&1
```

---

## 6. 后端服务部署

### 6.1 拉取代码

```bash
# 进入用户主目录
cd ~

# 克隆仓库（使用你的实际仓库地址）
git clone https://github.com/your-username/Cshine.git
cd Cshine/backend
```

### 6.2 创建虚拟环境

```bash
# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 6.3 配置环境变量

```bash
# 创建生产环境配置
cat > .env << 'EOF'
# 应用配置
APP_NAME=Cshine
APP_ENV=production
DEBUG=False

# 数据库配置（PostgreSQL）
DATABASE_URL=postgresql://cshine_user:your_strong_password_here@localhost:5432/cshine

# JWT 配置
SECRET_KEY=your_secret_key_change_this_in_production_must_be_very_long_and_random
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7

# 微信小程序配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret

# 阿里云 OSS 配置
ALIYUN_OSS_ACCESS_KEY_ID=your_access_key_id
ALIYUN_OSS_ACCESS_KEY_SECRET=your_access_key_secret
ALIYUN_OSS_BUCKET=your_bucket_name
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_DOMAIN=https://your-bucket.oss-cn-hangzhou.aliyuncs.com

# 阿里云通义听悟配置
ALIYUN_TINGWU_APP_KEY=your_tingwu_app_key
ALIYUN_TINGWU_ACCESS_KEY_ID=your_tingwu_access_key_id
ALIYUN_TINGWU_ACCESS_KEY_SECRET=your_tingwu_access_key_secret

# 文件上传配置
UPLOAD_DIR=/home/cshine/Cshine/backend/uploads
MAX_UPLOAD_SIZE=524288000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/home/cshine/Cshine/backend/logs/cshine.log

# CORS 配置
CORS_ORIGINS=["https://api.cshine.com", "https://servicewechat.com"]
EOF

# 设置文件权限
chmod 600 .env
```

**⚠️ 重要提示**：
- 必须修改 `SECRET_KEY` 为随机字符串
- 填入真实的微信小程序 AppID 和 AppSecret
- 填入阿里云 OSS 和通义听悟的密钥
- 数据库密码要与前面设置的一致

### 6.4 生成安全密钥

```bash
# 生成 SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 6.5 数据库迁移

```bash
# 运行数据库迁移
python main.py

# 检查数据库表是否创建成功
PGPASSWORD='your_db_password' psql -h localhost -U cshine_user -d cshine -c "\dt"
```

### 6.6 配置 Systemd 服务

创建服务文件：

```bash
sudo vim /etc/systemd/system/cshine-api.service
```

内容如下：

```ini
[Unit]
Description=Cshine FastAPI Application
After=network.target postgresql.service

[Service]
Type=notify
User=cshine
Group=cshine
WorkingDirectory=/home/cshine/Cshine/backend
Environment="PATH=/home/cshine/Cshine/backend/venv/bin"
ExecStart=/home/cshine/Cshine/backend/venv/bin/uvicorn main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log \
    --use-colors

# 重启策略
Restart=always
RestartSec=10

# 安全配置
NoNewPrivileges=true
PrivateTmp=true

# 日志
StandardOutput=append:/home/cshine/Cshine/backend/logs/uvicorn.log
StandardError=append:/home/cshine/Cshine/backend/logs/uvicorn.error.log

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start cshine-api

# 设置开机自启
sudo systemctl enable cshine-api

# 查看状态
sudo systemctl status cshine-api

# 查看日志
sudo journalctl -u cshine-api -f
```

### 6.7 测试 API

```bash
# 测试健康检查接口
curl http://127.0.0.1:8000/health

# 预期输出：
# {"status":"ok","message":"Service is running"}
```

---

## 7. Nginx 配置

### 7.1 创建配置文件

```bash
sudo vim /etc/nginx/sites-available/cshine
```

内容如下：

```nginx
# Upstream 配置
upstream cshine_api {
    server 127.0.0.1:8000;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name api.cshine.com;

    # Let's Encrypt 验证
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 其他请求重定向到 HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.cshine.com;

    # SSL 证书配置（先用 Let's Encrypt 自动配置，这里是示例）
    ssl_certificate /etc/letsencrypt/live/api.cshine.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.cshine.com/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 客户端上传大小限制（500MB，与微信小程序一致）
    client_max_body_size 500M;

    # 超时配置
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;

    # 日志
    access_log /var/log/nginx/cshine_access.log;
    error_log /var/log/nginx/cshine_error.log;

    # API 请求代理到 FastAPI
    location / {
        proxy_pass http://cshine_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件（如果需要直接提供）
    location /static/ {
        alias /home/cshine/Cshine/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件（如果不用 OSS）
    location /uploads/ {
        alias /home/cshine/Cshine/backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        proxy_pass http://cshine_api/health;
        access_log off;
    }
}
```

### 7.2 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/cshine /etc/nginx/sites-enabled/

# 删除默认配置（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 7.3 申请 SSL 证书

```bash
# 使用 Certbot 自动配置
sudo certbot --nginx -d api.cshine.com

# 测试自动续期
sudo certbot renew --dry-run
```

### 7.4 配置日志轮转

```bash
sudo vim /etc/logrotate.d/cshine
```

内容：

```
/var/log/nginx/cshine_*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}

/home/cshine/Cshine/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 cshine cshine
    missingok
}
```

---

## 8. 微信小程序配置

### 8.1 修改前端 API 地址

编辑 `utils/config.js`：

```javascript
// utils/config.js
const ENV = 'production'; // 'development' | 'production'

const API_CONFIG = {
  development: {
    baseURL: 'http://localhost:8000',
  },
  production: {
    baseURL: 'https://api.cshine.com',  // 修改为你的生产域名
  }
};

module.exports = {
  API_BASE_URL: API_CONFIG[ENV].baseURL,
  TIMEOUT: 30000,
  // ... 其他配置
};
```

### 8.2 配置服务器域名

登录微信公众平台：https://mp.weixin.qq.com/

1. 进入"开发" → "开发管理" → "开发设置"
2. 配置服务器域名：

**request 合法域名**：
```
https://api.cshine.com
```

**uploadFile 合法域名**：
```
https://api.cshine.com
https://your-bucket.oss-cn-hangzhou.aliyuncs.com  # 阿里云 OSS
```

**downloadFile 合法域名**：
```
https://api.cshine.com
https://your-bucket.oss-cn-hangzhou.aliyuncs.com  # 阿里云 OSS
```

**⚠️ 注意**：
- 域名必须备案
- 必须使用 HTTPS
- 不支持 IP 地址和端口号

### 8.3 上传代码审核

```bash
# 1. 在微信开发者工具中打开项目
# 2. 修改 project.config.json 中的 appid
# 3. 点击"上传"按钮
# 4. 填写版本号和项目备注
# 5. 提交审核
```

### 8.4 小程序审核要点

**必须提供**：
- 隐私政策链接
- 用户协议链接
- 联系方式
- 功能说明

**常见驳回原因**：
- 未提供测试账号
- 功能描述不清晰
- 涉及未开通的服务类目
- 缺少必要的用户协议

---

## 9. 监控与日志

### 9.1 服务器监控

#### 安装监控工具

```bash
# 安装 htop（进程监控）
sudo apt install htop -y

# 使用
htop
```

#### 资源使用情况

```bash
# CPU 和内存
free -h
top

# 磁盘使用
df -h

# 网络流量
sudo apt install nethogs -y
sudo nethogs
```

### 9.2 应用日志

```bash
# 查看 FastAPI 日志
tail -f ~/Cshine/backend/logs/cshine.log

# 查看 Uvicorn 日志
sudo journalctl -u cshine-api -f

# 查看 Nginx 日志
tail -f /var/log/nginx/cshine_access.log
tail -f /var/log/nginx/cshine_error.log
```

### 9.3 错误告警（可选）

使用云监控服务：
- **阿里云云监控**：免费基础监控
- **腾讯云云监控**：免费基础监控
- **第三方**：Sentry（错误追踪）

---

## 10. 备份策略

### 10.1 数据库备份

已在第 5.4 节配置了自动备份脚本。

### 10.2 文件备份

```bash
# 创建文件备份脚本
cat > ~/backup_files.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/cshine/files"
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="/home/cshine/Cshine/backend/uploads"

mkdir -p $BACKUP_DIR

# 打包上传文件
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" -C "$SOURCE_DIR" .

# 保留最近 7 天
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Files backup completed: uploads_$DATE.tar.gz"
EOF

chmod +x ~/backup_files.sh

# 添加到定时任务（每天凌晨3点）
crontab -e
# 0 3 * * * /home/cshine/backup_files.sh >> /home/cshine/backup.log 2>&1
```

### 10.3 代码备份

```bash
# 定期拉取最新代码
cd ~/Cshine
git pull origin main
```

---

## 11. 更新与维护

### 11.1 快速更新 ⭐

**一键更新命令**（最常用）：

```bash
# SSH 登录服务器
ssh cshine@your_server_ip

# 运行更新脚本
cd ~/Cshine/backend
bash deploy/update.sh
```

**更新过程**（自动完成）：
1. ✅ 备份当前代码和配置
2. ✅ 拉取最新代码
3. ✅ 检测并更新依赖
4. ✅ 运行数据库迁移
5. ✅ 重启服务
6. ✅ 健康检查

**耗时**: 1-2 分钟  
**停机时间**: < 5 秒

### 11.2 三种更新方式

#### 方式 1：标准更新（最常用）

```bash
bash deploy/update.sh
```

- 适用于：正常功能迭代、Bug 修复
- 特点：完整的更新流程，包含所有安全检查

#### 方式 2：热修复（紧急情况）

```bash
bash deploy/hotfix.sh
```

- 适用于：线上紧急修复，直接在服务器上修改代码
- 特点：不拉取代码，仅重启服务

#### 方式 3：快速回滚（出问题时）

```bash
bash deploy/rollback.sh
```

- 适用于：更新后发现问题，需要快速恢复
- 特点：自动回退到上一个版本

### 11.3 完整更新流程

```
┌──────────────┐
│ 1. 本地开发   │
│    提交代码   │
└───────┬──────┘
        │
        ▼
┌──────────────┐
│ 2. 推送到Git │
└───────┬──────┘
        │
        ▼
┌──────────────┐
│ 3. 登录服务器 │
└───────┬──────┘
        │
        ▼
┌──────────────┐
│ 4. 运行更新   │
│ update.sh    │
└───────┬──────┘
        │
        ├──► 备份
        ├──► 拉取代码
        ├──► 更新依赖
        ├──► 数据库迁移
        ├──► 重启服务
        └──► 健康检查
        │
        ▼
┌──────────────┐
│ 5. 验证功能  │
└──────────────┘
```

### 11.4 更新最佳实践

1. **选择合适时间**
   - 🌙 低峰期更新（如凌晨 2-4 点）
   - 📅 避开业务高峰期
   - 📢 提前通知用户

2. **小步快跑**
   - 📦 频繁发布小更新
   - ✅ 每次只包含相关修改
   - 🔍 更容易定位问题

3. **备份优先**
   - 💾 更新前自动备份
   - 📂 保留最近 7 天的备份
   - 🔙 随时可以快速回滚

4. **充分测试**
   - 🧪 本地测试通过
   - 🔬 测试服务器验证
   - ✅ 生产环境灰度发布

### 11.5 监控更新状态

```bash
# 查看服务状态
sudo systemctl status cshine-api

# 查看实时日志
tail -f ~/Cshine/backend/logs/cshine.log

# 查看系统日志
sudo journalctl -u cshine-api -f

# 测试 API
curl https://api.cshine.com/health
```

### 11.6 日常维护任务

**每天**：
- 📊 检查服务状态
- 📝 查看错误日志
- 💾 自动数据库备份（已配置）

**每周**：
- 🔄 代码更新
- 📈 性能监控
- 🧹 清理旧日志

**每月**：
- 🔐 更新系统安全补丁
- 💿 完整备份验证
- 📊 性能优化检查

**详细更新指南**: 查看 `backend/deploy/UPDATE_GUIDE.md`

---

## 12. 常见问题

### 12.1 服务无法启动

```bash
# 查看详细错误
sudo journalctl -u cshine-api -n 50

# 检查端口占用
sudo lsof -i :8000

# 手动测试
cd ~/Cshine/backend
source venv/bin/activate
python main.py
```

### 12.2 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 检查连接
PGPASSWORD='your_password' psql -h localhost -U cshine_user -d cshine

# 查看日志
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

### 12.3 Nginx 502 错误

```bash
# 检查 FastAPI 是否运行
sudo systemctl status cshine-api

# 检查 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/cshine_error.log
```

### 12.4 SSL 证书问题

```bash
# 检查证书有效期
sudo certbot certificates

# 强制续期
sudo certbot renew --force-renewal

# 重启 Nginx
sudo systemctl reload nginx
```

### 12.5 文件上传失败

```bash
# 检查目录权限
ls -la ~/Cshine/backend/uploads

# 修复权限
sudo chown -R cshine:cshine ~/Cshine/backend/uploads
sudo chmod -R 755 ~/Cshine/backend/uploads

# 检查磁盘空间
df -h
```

### 12.6 性能优化

```bash
# 调整 Uvicorn workers 数量
# 编辑 systemd 服务文件
sudo vim /etc/systemd/system/cshine-api.service

# 修改 --workers 参数：
# workers = (2 * CPU 核心数) + 1
# 例如 4 核 CPU：--workers 9

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart cshine-api
```

---

## 📋 部署检查清单

**服务器准备**
- [ ] 购买云服务器
- [ ] 购买域名
- [ ] 域名备案通过
- [ ] 配置 DNS 解析
- [ ] 防火墙配置完成

**环境配置**
- [ ] Python 3.11 安装
- [ ] PostgreSQL 安装配置
- [ ] Nginx 安装配置
- [ ] SSL 证书配置
- [ ] 系统用户创建

**应用部署**
- [ ] 代码拉取成功
- [ ] 虚拟环境创建
- [ ] 依赖安装完成
- [ ] 环境变量配置
- [ ] 数据库迁移完成
- [ ] Systemd 服务配置
- [ ] 服务启动成功

**Nginx 配置**
- [ ] 配置文件创建
- [ ] HTTPS 配置
- [ ] 反向代理配置
- [ ] 日志轮转配置

**微信小程序**
- [ ] API 地址修改
- [ ] 服务器域名配置
- [ ] 代码上传测试
- [ ] 提交审核

**监控备份**
- [ ] 日志配置
- [ ] 数据库备份脚本
- [ ] 文件备份脚本
- [ ] 定时任务配置

**测试验证**
- [ ] 健康检查接口
- [ ] 登录接口测试
- [ ] 文件上传测试
- [ ] AI 功能测试
- [ ] 小程序端到端测试

---

## 🚀 快速部署命令总结

```bash
# === 1. 服务器初始化 ===
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv nginx postgresql git

# === 2. 配置数据库 ===
sudo -u postgres psql -c "CREATE DATABASE cshine;"
sudo -u postgres psql -c "CREATE USER cshine_user WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cshine TO cshine_user;"

# === 3. 部署代码 ===
cd ~
git clone https://github.com/your-username/Cshine.git
cd Cshine/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# === 4. 配置环境变量 ===
# 编辑 .env 文件

# === 5. 启动服务 ===
sudo systemctl start cshine-api
sudo systemctl enable cshine-api

# === 6. 配置 Nginx ===
sudo certbot --nginx -d api.cshine.com
sudo systemctl reload nginx

# === 7. 验证 ===
curl https://api.cshine.com/health
```

---

## 📞 技术支持

如遇到问题，可以：
1. 查看日志排查
2. 参考本文档的"常见问题"章节
3. 提交 GitHub Issue

---

**祝部署顺利！🎉**

---

**文档版本**: v1.0  
**更新日期**: 2025-11-08  
**作者**: Cshine Team

