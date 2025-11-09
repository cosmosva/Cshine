#!/bin/bash
#
# Cshine 回滚脚本
# 用法: ./rollback_upload_feature.sh
#

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
BACKUP_DIR="$BACKEND_DIR/backups"

echo -e "${RED}"
echo "╔════════════════════════════════════════════╗"
echo "║          ⚠️  紧急回滚脚本                  ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$BACKEND_DIR"

# 列出可用的备份
echo -e "${YELLOW}可用的数据库备份:${NC}"
echo ""

if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
    echo -e "${RED}❌ 未找到备份文件${NC}"
    exit 1
fi

ls -lht "$BACKUP_DIR"/cshine.db.backup.* | head -10
echo ""

# 选择备份
read -p "请输入要恢复的备份文件名（或按 Ctrl+C 取消）: " BACKUP_NAME

if [ -z "$BACKUP_NAME" ]; then
    echo -e "${RED}❌ 未指定备份文件${NC}"
    exit 1
fi

BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME"

if [ ! -f "$BACKUP_FILE" ]; then
    # 尝试自动补全路径
    if [ -f "$BACKUP_NAME" ]; then
        BACKUP_FILE="$BACKUP_NAME"
    else
        echo -e "${RED}❌ 备份文件不存在: $BACKUP_FILE${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${RED}⚠️  警告: 即将执行回滚操作${NC}"
echo "备份文件: $BACKUP_FILE"
echo "当前数据库将被覆盖！"
echo ""
read -p "确认回滚? (输入 'YES' 继续): " CONFIRM

if [ "$CONFIRM" != "YES" ]; then
    echo -e "${YELLOW}❌ 已取消回滚${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}开始回滚...${NC}"

# 步骤 1: 备份当前数据库
echo -e "${YELLOW}[1/4] 备份当前数据库...${NC}"
SAFETY_BACKUP="$BACKUP_DIR/cshine.db.before_rollback.$(date +%Y%m%d_%H%M%S)"
if [ -f "cshine.db" ]; then
    cp cshine.db "$SAFETY_BACKUP"
    echo -e "${GREEN}✅ 当前数据库已备份到: $SAFETY_BACKUP${NC}"
fi

# 步骤 2: 停止服务
echo -e "${YELLOW}[2/4] 停止服务...${NC}"
if command -v systemctl &> /dev/null && systemctl is-active --quiet cshine; then
    sudo systemctl stop cshine
    echo -e "${GREEN}✅ systemd 服务已停止${NC}"
elif [ -f "server.pid" ]; then
    PID=$(cat server.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        sleep 2
        echo -e "${GREEN}✅ 进程已停止 (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  进程未运行${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未检测到运行中的服务${NC}"
fi

# 步骤 3: 恢复数据库
echo -e "${YELLOW}[3/4] 恢复数据库...${NC}"
cp "$BACKUP_FILE" cshine.db
echo -e "${GREEN}✅ 数据库已恢复${NC}"

# 步骤 4: 启动服务
echo -e "${YELLOW}[4/4] 启动服务...${NC}"
if command -v systemctl &> /dev/null; then
    sudo systemctl start cshine
    sleep 2
    if systemctl is-active --quiet cshine; then
        echo -e "${GREEN}✅ 服务已启动${NC}"
    else
        echo -e "${RED}❌ 服务启动失败${NC}"
        sudo systemctl status cshine --no-pager
        exit 1
    fi
else
    source venv/bin/activate
    nohup python main.py > server.log 2>&1 &
    echo $! > server.pid
    sleep 3
    echo -e "${GREEN}✅ 服务已启动 (PID: $(cat server.pid))${NC}"
fi

# 验证
echo ""
echo -e "${YELLOW}验证服务状态...${NC}"
sleep 2

HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 服务健康检查通过${NC}"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ 回滚成功！                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}📋 回滚信息:${NC}"
    echo "  • 恢复的备份: $BACKUP_FILE"
    echo "  • 回滚前备份: $SAFETY_BACKUP"
    echo "  • 服务状态: 运行中"
    echo ""
else
    echo -e "${RED}❌ 服务健康检查失败${NC}"
    tail -20 logs/cshine.log 2>/dev/null || tail -20 server.log
    exit 1
fi

