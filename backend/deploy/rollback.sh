#!/bin/bash
# Cshine 后端回滚脚本
# 快速回滚到上一个版本

set -e

echo "=========================================="
echo "  ⏮️  Cshine 后端回滚"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "main.py" ]; then
    echo "❌ 请在 backend 目录下运行此脚本"
    echo "运行: cd ~/Cshine/backend && bash deploy/rollback.sh"
    exit 1
fi

cd ~/Cshine

echo "📋 最近的提交记录："
git log --oneline -10
echo ""

echo "📋 当前版本："
git log --oneline -1
echo ""

read -p "回滚到上一个版本？(y/N): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 取消回滚"
    exit 0
fi

echo ""
echo "📦 步骤 1/4: 停止服务..."
sudo systemctl stop cshine-api
echo "✅ 服务已停止"
echo ""

echo "📦 步骤 2/4: 回滚代码..."
git reset --hard HEAD~1
echo "✅ 代码已回滚"
echo ""

echo "📦 步骤 3/4: 恢复依赖（如果需要）..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
echo "✅ 依赖已恢复"
echo ""

echo "📦 步骤 4/4: 重启服务..."
sudo systemctl start cshine-api

# 等待服务启动
sleep 3

if systemctl is-active --quiet cshine-api; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败！请检查日志"
    sudo journalctl -u cshine-api -n 30 --no-pager
    exit 1
fi
echo ""

echo "=========================================="
echo "  ✅ 回滚完成！"
echo "=========================================="
echo ""
echo "📋 当前版本："
git log --oneline -1
echo ""

