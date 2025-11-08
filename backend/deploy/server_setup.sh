#!/bin/bash
# Cshine 服务器环境自动化安装脚本
# 适用于 Ubuntu 22.04 LTS

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  Cshine 服务器环境安装脚本"
echo "=========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 root 权限运行此脚本"
    echo "运行: sudo bash server_setup.sh"
    exit 1
fi

echo "📦 步骤 1/8: 更新系统软件包..."
apt update
apt upgrade -y

echo "✅ 系统更新完成"
echo ""

echo "📦 步骤 2/8: 安装基础工具..."
apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    unzip \
    build-essential \
    software-properties-common \
    ufw

echo "✅ 基础工具安装完成"
echo ""

echo "📦 步骤 3/8: 安装 Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.11 python3.11-venv python3.11-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# 验证安装
PYTHON_VERSION=$(python3.11 --version)
echo "✅ Python 安装完成: $PYTHON_VERSION"
echo ""

echo "📦 步骤 4/8: 安装 Nginx..."
apt install -y nginx
systemctl start nginx
systemctl enable nginx

echo "✅ Nginx 安装完成"
echo ""

echo "📦 步骤 5/8: 安装 PostgreSQL..."
apt install -y postgresql postgresql-contrib
systemctl start postgresql
systemctl enable postgresql

echo "✅ PostgreSQL 安装完成"
echo ""

echo "📦 步骤 6/8: 配置防火墙..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

echo "✅ 防火墙配置完成"
echo ""

echo "📦 步骤 7/8: 安装 Certbot (Let's Encrypt)..."
apt install -y certbot python3-certbot-nginx

echo "✅ Certbot 安装完成"
echo ""

echo "📦 步骤 8/8: 创建部署用户..."
if id "cshine" &>/dev/null; then
    echo "⚠️  用户 cshine 已存在，跳过创建"
else
    adduser --disabled-password --gecos "" cshine
    usermod -aG sudo cshine
    echo "✅ 用户 cshine 创建完成"
fi

echo ""
echo "=========================================="
echo "  🎉 环境安装完成！"
echo "=========================================="
echo ""
echo "📋 后续步骤："
echo "1. 配置数据库"
echo "   sudo -u postgres psql"
echo "   CREATE DATABASE cshine;"
echo "   CREATE USER cshine_user WITH PASSWORD 'your_password';"
echo "   GRANT ALL PRIVILEGES ON DATABASE cshine TO cshine_user;"
echo ""
echo "2. 切换到 cshine 用户"
echo "   su - cshine"
echo ""
echo "3. 克隆代码仓库"
echo "   git clone https://github.com/your-username/Cshine.git"
echo ""
echo "4. 运行应用部署脚本"
echo "   cd Cshine/backend/deploy"
echo "   bash app_deploy.sh"
echo ""
echo "=========================================="

