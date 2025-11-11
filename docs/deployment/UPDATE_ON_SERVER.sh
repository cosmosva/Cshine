#!/bin/bash
# Cshine 服务器端更新脚本
# 直接在服务器上执行
# 使用方法: bash docs/deployment/UPDATE_ON_SERVER.sh

set -e

echo "=========================================="
echo "  🚀 Cshine 后端更新 v0.5.5 → v0.5.15"
echo "=========================================="
echo ""

# 检查是否在项目目录
if [ ! -f "backend/main.py" ]; then
    echo "❌ 错误：请在项目根目录执行此脚本"
    echo "   cd /home/cshine/Cshine"
    echo "   bash docs/deployment/UPDATE_ON_SERVER.sh"
    exit 1
fi

echo "=========================================="
echo "📦 步骤 1/6: 检查当前状态"
echo "=========================================="
echo "✅ 当前目录: $(pwd)"
echo "✅ 当前分支: $(git branch --show-current)"
echo "✅ 当前版本: $(git log --oneline -1)"
echo ""

echo "=========================================="
echo "📦 步骤 2/6: 备份数据库"
echo "=========================================="
cd backend

# PostgreSQL 备份
BACKUP_FILE="backup_before_v0.5.15_$(date +%Y%m%d_%H%M%S).sql"
echo "正在备份 PostgreSQL 数据库..."
sudo -u postgres pg_dump cshine_db > "$BACKUP_FILE" 2>/dev/null || {
    echo "⚠️  PostgreSQL 备份失败，继续执行..."
}

if [ -f "$BACKUP_FILE" ]; then
    echo "✅ 数据库已备份到: backend/$BACKUP_FILE"
else
    echo "⚠️  未找到备份文件"
fi

cd ..
echo ""

echo "=========================================="
echo "📦 步骤 3/6: 拉取最新代码"
echo "=========================================="
OLD_COMMIT=$(git log --oneline -1)
git fetch origin
git pull origin main
NEW_COMMIT=$(git log --oneline -1)

echo "✅ 代码更新完成"
echo "   更新前: $OLD_COMMIT"
echo "   更新后: $NEW_COMMIT"
echo ""

echo "=========================================="
echo "📦 步骤 4/6: 执行数据库迁移"
echo "=========================================="
cd backend

# 激活虚拟环境
if [ -d "../venv" ]; then
    source ../venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，尝试使用系统 Python"
fi

# 执行 PostgreSQL 迁移
echo "正在执行数据库迁移..."
if [ -f "migrations/add_contacts_and_speakers.py" ]; then
    python migrations/add_contacts_and_speakers.py
    echo "✅ 数据库迁移完成"
else
    echo "⚠️  未找到迁移脚本"
fi

cd ..
echo ""

echo "=========================================="
echo "📦 步骤 5/6: 重启后端服务"
echo "=========================================="
sudo systemctl restart cshine-api
sleep 3
echo "✅ 服务已重启"
echo ""

echo "=========================================="
echo "📦 步骤 6/6: 验证服务状态"
echo "=========================================="

# 检查服务状态
if sudo systemctl is-active --quiet cshine-api; then
    echo "✅ 服务运行正常"
else
    echo "❌ 服务未运行"
    sudo systemctl status cshine-api
    exit 1
fi

# 检查健康接口
sleep 2
HEALTH_CHECK=$(curl -s http://localhost:8000/health || echo "failed")
if [[ "$HEALTH_CHECK" == *"healthy"* ]]; then
    echo "✅ 健康检查通过"
else
    echo "❌ 健康检查失败: $HEALTH_CHECK"
fi

# 验证数据库表
echo ""
echo "验证数据库表..."
TABLE_CHECK=$(sudo -u postgres psql cshine_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('contacts', 'meeting_speakers');" 2>/dev/null || echo "0")
if [ "$TABLE_CHECK" -eq 2 ]; then
    echo "✅ 新表已创建（contacts, meeting_speakers）"
else
    echo "⚠️  新表验证失败（找到 $TABLE_CHECK 个表）"
fi

# 验证新字段
COLUMN_CHECK=$(sudo -u postgres psql cshine_db -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'meetings' AND column_name = 'transcript_paragraphs';" 2>/dev/null || echo "0")
if [ "$COLUMN_CHECK" -eq 1 ]; then
    echo "✅ 新字段已添加（transcript_paragraphs）"
else
    echo "⚠️  新字段验证失败"
fi

echo ""
echo "=========================================="
echo "  ✅ 更新完成！"
echo "=========================================="
echo ""
echo "📊 更新摘要:"
echo "   - 版本: v0.5.5 → v0.5.15"
echo "   - 新增表: contacts, meeting_speakers"
echo "   - 新增字段: meetings.transcript_paragraphs"
echo "   - 服务状态: 运行中"
echo ""
echo "📝 后续步骤:"
echo "   1. 查看服务日志: sudo journalctl -u cshine-api -f --lines=50"
echo "   2. 测试上传功能"
echo "   3. 测试摘要生成"
echo "   4. 测试思维导图"
echo ""
echo "📖 详细文档: docs/deployment/DEPLOY_v0.5.15_20251111.md"
echo ""

