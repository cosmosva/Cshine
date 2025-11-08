#!/bin/bash
# Cshine 后端更新脚本
# 自动拉取代码、安装依赖、运行迁移、重启服务

set -e

echo "=========================================="
echo "  🚀 Cshine 后端更新"
echo "=========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "main.py" ]; then
    echo "❌ 请在 backend 目录下运行此脚本"
    echo "运行: cd ~/Cshine/backend && bash deploy/update.sh"
    exit 1
fi

# 检查是否为 cshine 用户
if [ "$USER" != "cshine" ]; then
    echo "⚠️  建议使用 cshine 用户运行此脚本"
    read -p "是否继续？(y/N): " confirm
    if [ "$confirm" != "y" ]; then
        exit 0
    fi
fi

echo "📦 步骤 1/6: 备份当前代码..."
BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r .env "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  没有找到 .env 文件"
cp -r logs "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  没有找到 logs 目录"
echo "✅ 备份完成: $BACKUP_DIR"
echo ""

echo "📦 步骤 2/6: 拉取最新代码..."
cd ~/Cshine

# 保存当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    echo "⚠️  检测到未提交的更改："
    git status -s
    read -p "是否暂存这些更改？(y/N): " stash_confirm
    if [ "$stash_confirm" = "y" ]; then
        git stash
        echo "✅ 更改已暂存"
    else
        echo "❌ 请先处理未提交的更改"
        exit 1
    fi
fi

# 拉取代码
git pull origin $CURRENT_BRANCH
echo "✅ 代码更新完成"
echo ""

echo "📦 步骤 3/6: 更新依赖..."
cd backend
source venv/bin/activate

# 检查 requirements.txt 是否有变化
if git diff HEAD@{1} HEAD -- requirements.txt | grep -q "^+"; then
    echo "检测到依赖变化，正在更新..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ 依赖更新完成"
else
    echo "✅ 依赖无变化，跳过更新"
fi
echo ""

echo "📦 步骤 4/6: 运行数据库迁移..."
# 检查是否有新的迁移脚本
if [ -d "migrations" ]; then
    migration_count=$(ls migrations/*.py 2>/dev/null | wc -l)
    if [ $migration_count -gt 0 ]; then
        echo "找到 $migration_count 个迁移脚本"
        read -p "是否运行所有迁移？(y/N): " migrate_confirm
        if [ "$migrate_confirm" = "y" ]; then
            for migration in migrations/*.py; do
                if [ -f "$migration" ]; then
                    echo "运行: $migration"
                    python "$migration" || echo "⚠️  迁移可能已经运行过"
                fi
            done
            echo "✅ 迁移完成"
        else
            echo "⚠️  跳过迁移"
        fi
    else
        echo "✅ 没有迁移脚本"
    fi
else
    echo "✅ 没有 migrations 目录"
fi
echo ""

echo "📦 步骤 5/6: 重启服务..."
sudo systemctl restart cshine-api

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 检查服务状态
if systemctl is-active --quiet cshine-api; then
    echo "✅ 服务启动成功"
else
    echo "❌ 服务启动失败！"
    echo "查看日志："
    sudo journalctl -u cshine-api -n 30 --no-pager
    echo ""
    echo "是否需要回滚？(y/N): "
    read rollback_confirm
    if [ "$rollback_confirm" = "y" ]; then
        bash deploy/rollback.sh
    fi
    exit 1
fi
echo ""

echo "📦 步骤 6/6: 健康检查..."
sleep 2

# 检查健康接口
HEALTH_CHECK=$(curl -s http://127.0.0.1:8000/health | grep -o '"status":"ok"' || echo "")

if [ -n "$HEALTH_CHECK" ]; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败"
    curl -s http://127.0.0.1:8000/health || echo "无法连接到服务"
    exit 1
fi
echo ""

echo "=========================================="
echo "  🎉 更新完成！"
echo "=========================================="
echo ""
echo "📋 更新摘要："
git log --oneline -5
echo ""
echo "📋 服务状态："
sudo systemctl status cshine-api --no-pager | head -10
echo ""
echo "📋 后续操作："
echo "   查看日志: sudo journalctl -u cshine-api -f"
echo "   查看应用日志: tail -f ~/Cshine/backend/logs/cshine.log"
echo "   回滚版本: bash deploy/rollback.sh"
echo ""
echo "=========================================="

