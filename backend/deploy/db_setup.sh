#!/bin/bash
# Cshine 数据库配置脚本

set -e

echo "=========================================="
echo "  Cshine 数据库配置"
echo "=========================================="
echo ""

# 提示输入数据库密码
read -sp "请输入数据库密码（cshine_user）: " DB_PASSWORD
echo ""

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ 密码不能为空"
    exit 1
fi

echo ""
echo "📦 正在配置数据库..."

# 配置数据库
sudo -u postgres psql << EOF
-- 删除已存在的数据库和用户（如果需要重新配置）
-- DROP DATABASE IF EXISTS cshine;
-- DROP USER IF EXISTS cshine_user;

-- 创建数据库
CREATE DATABASE cshine;

-- 创建用户
CREATE USER cshine_user WITH PASSWORD '$DB_PASSWORD';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE cshine TO cshine_user;

-- 退出
\q
EOF

echo "✅ 数据库配置完成"
echo ""
echo "📋 数据库信息："
echo "   数据库名: cshine"
echo "   用户名: cshine_user"
echo "   密码: ********"
echo "   主机: localhost"
echo "   端口: 5432"
echo ""
echo "📝 连接字符串（用于 .env 文件）："
echo "DATABASE_URL=postgresql://cshine_user:$DB_PASSWORD@localhost:5432/cshine"
echo ""
echo "⚠️  请妥善保管数据库密码！"
echo ""

