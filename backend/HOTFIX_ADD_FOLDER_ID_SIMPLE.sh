#!/bin/bash

# 🚨 紧急修复脚本（简化版）：添加 folder_id 字段到线上数据库
# 用途：修复 v0.5.5 部署后缺少 folder_id 字段的问题
# 运行：bash backend/HOTFIX_ADD_FOLDER_ID_SIMPLE.sh

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

# 查找 Python 可执行文件
echo "🔍 查找 Python..."
PYTHON_CMD=""

# 尝试多种方式找到 Python
if [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_ROOT/venv/bin/python"
    echo "✅ 找到虚拟环境 Python: $PYTHON_CMD"
elif [ -f "$BACKEND_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$BACKEND_DIR/venv/bin/python"
    echo "✅ 找到虚拟环境 Python: $PYTHON_CMD"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "✅ 使用系统 Python3: $(which python3)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo "✅ 使用系统 Python: $(which python)"
else
    echo "❌ 错误：找不到 Python"
    exit 1
fi
echo ""

# 检查 Python 版本
echo "🐍 Python 版本："
$PYTHON_CMD --version
echo ""

# 检查必要的 Python 包
echo "📦 检查依赖包..."
$PYTHON_CMD -c "import sqlalchemy; import psycopg2; from loguru import logger" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 所有依赖包已安装"
else
    echo "⚠️  警告：某些依赖包可能缺失，但会尝试继续..."
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

# 执行迁移
echo "🚀 执行数据库迁移..."
echo "   Python: $PYTHON_CMD"
echo "   脚本: $MIGRATION_SCRIPT"
echo ""

$PYTHON_CMD "$MIGRATION_SCRIPT"

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
    echo "   4. 手动执行：$PYTHON_CMD $MIGRATION_SCRIPT"
    echo ""
    exit 1
fi

