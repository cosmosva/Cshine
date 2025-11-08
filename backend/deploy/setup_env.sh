#!/bin/bash
# 环境变量配置脚本

echo "配置环境变量..."
echo ""

# 生成随机 SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

# 交互式输入
echo "请输入以下配置信息："
echo ""

read -p "数据库密码: " DB_PASSWORD
read -p "微信小程序 AppID: " WECHAT_APP_ID
read -p "微信小程序 AppSecret: " WECHAT_APP_SECRET
read -p "阿里云 OSS AccessKeyId: " OSS_ACCESS_KEY_ID
read -p "阿里云 OSS AccessKeySecret: " OSS_ACCESS_KEY_SECRET
read -p "阿里云 OSS Bucket 名称: " OSS_BUCKET
read -p "阿里云 OSS Endpoint (如: oss-cn-hangzhou.aliyuncs.com): " OSS_ENDPOINT
read -p "通义听悟 AppKey: " TINGWU_APP_KEY
read -p "通义听悟 AccessKeyId: " TINGWU_ACCESS_KEY_ID
read -p "通义听悟 AccessKeySecret: " TINGWU_ACCESS_KEY_SECRET

echo ""
echo "正在生成 .env 文件..."

cat > .env << EOF
# 应用配置
APP_NAME=Cshine
APP_ENV=production
DEBUG=False

# 数据库配置
DATABASE_URL=postgresql://cshine_user:${DB_PASSWORD}@localhost:5432/cshine

# JWT 配置
SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7

# 微信小程序配置
WECHAT_APPID=${WECHAT_APP_ID}
WECHAT_SECRET=${WECHAT_APP_SECRET}

# 阿里云 OSS 配置
OSS_ACCESS_KEY_ID=${OSS_ACCESS_KEY_ID}
OSS_ACCESS_KEY_SECRET=${OSS_ACCESS_KEY_SECRET}
OSS_BUCKET_NAME=${OSS_BUCKET}
OSS_ENDPOINT=${OSS_ENDPOINT}

# 阿里云通义听悟配置
TINGWU_APP_KEY=${TINGWU_APP_KEY}
ALIBABA_CLOUD_ACCESS_KEY_ID=${TINGWU_ACCESS_KEY_ID}
ALIBABA_CLOUD_ACCESS_KEY_SECRET=${TINGWU_ACCESS_KEY_SECRET}

# 文件上传配置
UPLOAD_DIR=/home/cshine/Cshine/backend/uploads
MAX_UPLOAD_SIZE=524288000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/home/cshine/Cshine/backend/logs/cshine.log

# CORS 配置
CORS_ORIGINS=["https://api.cshine.com", "https://servicewechat.com"]
EOF

chmod 600 .env

echo "✅ .env 文件创建完成"
echo ""
echo "⚠️  请妥善保管 .env 文件，不要提交到 Git！"

