#!/bin/bash
# Cshine 热修复脚本
# 快速修复并重启，不拉取代码（适用于紧急修复）

set -e

echo "=========================================="
echo "  🔥 Cshine 热修复"
echo "=========================================="
echo ""

if [ ! -f "main.py" ]; then
    echo "❌ 请在 backend 目录下运行此脚本"
    exit 1
fi

echo "⚠️  热修复模式："
echo "   - 不拉取远程代码"
echo "   - 仅重新安装依赖（如果需要）"
echo "   - 运行数据库迁移"
echo "   - 重启服务"
echo ""

read -p "是否继续？(y/N): " confirm
if [ "$confirm" != "y" ]; then
    exit 0
fi

echo ""
echo "📦 步骤 1/3: 检查依赖..."
source venv/bin/activate

read -p "是否重新安装依赖？(y/N): " deps_confirm
if [ "$deps_confirm" = "y" ]; then
    pip install -r requirements.txt
    echo "✅ 依赖已更新"
else
    echo "✅ 跳过依赖更新"
fi
echo ""

echo "📦 步骤 2/3: 数据库迁移（可选）..."
read -p "是否运行迁移？(y/N): " migrate_confirm
if [ "$migrate_confirm" = "y" ]; then
    for migration in migrations/*.py; do
        if [ -f "$migration" ]; then
            echo "运行: $migration"
            python "$migration" || echo "⚠️  迁移可能已运行"
        fi
    done
    echo "✅ 迁移完成"
else
    echo "✅ 跳过迁移"
fi
echo ""

echo "📦 步骤 3/3: 重启服务..."
sudo systemctl restart cshine-api

sleep 3

if systemctl is-active --quiet cshine-api; then
    echo "✅ 服务重启成功"
    
    # 健康检查
    HEALTH=$(curl -s http://127.0.0.1:8000/health | grep -o '"status":"ok"' || echo "")
    if [ -n "$HEALTH" ]; then
        echo "✅ 健康检查通过"
    else
        echo "⚠️  健康检查失败"
    fi
else
    echo "❌ 服务启动失败"
    sudo journalctl -u cshine-api -n 20 --no-pager
    exit 1
fi
echo ""

echo "=========================================="
echo "  ✅ 热修复完成！"
echo "=========================================="

