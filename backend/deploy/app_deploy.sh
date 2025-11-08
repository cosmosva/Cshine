#!/bin/bash
# Cshine 应用部署脚本（在 cshine 用户下运行）

set -e

echo "=========================================="
echo "  Cshine 应用部署"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 请在 backend 目录下运行此脚本"
    echo "运行: cd ~/Cshine/backend && bash deploy/app_deploy.sh"
    exit 1
fi

echo "📦 步骤 1/6: 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    python3.11 -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

echo ""
echo "📦 步骤 2/6: 安装依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ 依赖安装完成"
echo ""

echo "📦 步骤 3/6: 配置环境变量..."
if [ -f ".env" ]; then
    echo "⚠️  .env 文件已存在"
    read -p "是否覆盖？(y/N): " confirm
    if [ "$confirm" != "y" ]; then
        echo "跳过 .env 配置"
    else
        bash deploy/setup_env.sh
    fi
else
    bash deploy/setup_env.sh
fi

echo ""
echo "📦 步骤 4/6: 创建必要目录..."
mkdir -p logs
mkdir -p uploads
chmod 755 logs uploads

echo "✅ 目录创建完成"
echo ""

echo "📦 步骤 5/6: 运行数据库迁移..."
python migrations/add_meeting_favorite_tags.py
python migrations/add_meeting_summary_types.py

echo "✅ 数据库迁移完成"
echo ""

echo "📦 步骤 6/6: 配置 Systemd 服务..."
echo "需要 sudo 权限来配置系统服务"

sudo bash deploy/setup_systemd.sh

echo ""
echo "=========================================="
echo "  🎉 应用部署完成！"
echo "=========================================="
echo ""
echo "📋 服务管理命令："
echo "   启动服务: sudo systemctl start cshine-api"
echo "   停止服务: sudo systemctl stop cshine-api"
echo "   重启服务: sudo systemctl restart cshine-api"
echo "   查看状态: sudo systemctl status cshine-api"
echo "   查看日志: sudo journalctl -u cshine-api -f"
echo ""
echo "📋 下一步："
echo "1. 配置 Nginx 反向代理"
echo "   sudo bash deploy/setup_nginx.sh"
echo ""
echo "2. 申请 SSL 证书"
echo "   sudo certbot --nginx -d api.cshine.com"
echo ""
echo "3. 测试 API"
echo "   curl https://api.cshine.com/health"
echo ""
echo "=========================================="

