#!/bin/bash

# 🚨 紧急修复脚本：添加 folder_id 字段到线上数据库
# 用途：修复 v0.5.5 部署后缺少 folder_id 字段的问题
# 运行：bash backend/HOTFIX_ADD_FOLDER_ID.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚨 紧急修复：添加 folder_id 字段"
echo "=========================================="
echo ""

# 切换到 backend 目录
cd "$(dirname "$0")"
BACKEND_DIR=$(pwd)
PROJECT_ROOT=$(dirname "$BACKEND_DIR")
echo "📂 Backend 目录: $BACKEND_DIR"
echo "📂 项目根目录: $PROJECT_ROOT"
echo ""

# 激活虚拟环境（尝试多个可能的位置）
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "🔧 激活虚拟环境（项目根目录）..."
    source "$PROJECT_ROOT/venv/bin/activate"
    echo "✅ 虚拟环境已激活"
elif [ -d "$BACKEND_DIR/venv" ]; then
    echo "🔧 激活虚拟环境（backend 目录）..."
    source "$BACKEND_DIR/venv/bin/activate"
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 错误：找不到虚拟环境"
    echo "   尝试的路径："
    echo "   - $PROJECT_ROOT/venv"
    echo "   - $BACKEND_DIR/venv"
    exit 1
fi
echo ""

# 检查数据库类型
echo "🔍 检查数据库配置..."
if grep -q "postgresql" .env 2>/dev/null || grep -q "postgres" .env 2>/dev/null; then
    echo "✅ 检测到 PostgreSQL 数据库"
    MIGRATION_SCRIPT="migrations/add_folders_and_folder_id_postgres.py"
else
    echo "✅ 检测到 SQLite 数据库"
    MIGRATION_SCRIPT="migrations/add_folders_and_folder_id.py"
fi
echo ""

# 备份数据库（PostgreSQL）
echo "💾 备份数据库..."
if [ -f "cshine.db" ]; then
    # SQLite 备份
    cp cshine.db "cshine.db.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ SQLite 数据库已备份"
elif command -v pg_dump &> /dev/null; then
    # PostgreSQL 备份（需要配置）
    echo "⚠️  PostgreSQL 备份需要手动执行"
    echo "   建议命令：pg_dump -U <user> -d <database> > backup.sql"
else
    echo "⚠️  跳过自动备份"
fi
echo ""

# 执行迁移
echo "🚀 执行数据库迁移..."
echo "   脚本：$MIGRATION_SCRIPT"
echo ""

python "$MIGRATION_SCRIPT"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 迁移成功！"
    echo "=========================================="
    echo ""
    echo "📋 后续步骤："
    echo "   1. 重启服务：sudo systemctl restart cshine-api"
    echo "   2. 检查状态：sudo systemctl status cshine-api"
    echo "   3. 查看日志：tail -50 logs/cshine.log"
    echo "   4. 测试功能：在小程序中测试知识库功能"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ 迁移失败！"
    echo "=========================================="
    echo ""
    echo "📋 排查步骤："
    echo "   1. 查看上方错误信息"
    echo "   2. 检查数据库连接配置"
    echo "   3. 确认数据库用户权限"
    echo "   4. 查看完整日志"
    echo ""
    exit 1
fi

