#!/bin/bash
#
# Cshine 上传功能一键部署脚本
# 用法: ./deploy_upload_feature.sh
#

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
BACKUP_DIR="$BACKEND_DIR/backups"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════╗"
echo "║   Cshine 上传功能部署脚本 v1.0           ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# 检查是否在正确的目录
if [ ! -f "$BACKEND_DIR/main.py" ]; then
    echo -e "${RED}❌ 错误：未找到 backend/main.py${NC}"
    echo "请确保在 Cshine 项目根目录运行此脚本"
    exit 1
fi

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# ==================== 步骤 1: 备份数据库 ====================
echo -e "${YELLOW}[1/6] 备份数据库...${NC}"
cd "$BACKEND_DIR"

if [ -f "cshine.db" ]; then
    BACKUP_FILE="$BACKUP_DIR/cshine.db.backup.$(date +%Y%m%d_%H%M%S)"
    cp cshine.db "$BACKUP_FILE"
    echo -e "${GREEN}✅ 数据库已备份到: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}⚠️  未找到数据库文件（首次部署？）${NC}"
fi

# ==================== 步骤 2: 拉取最新代码 ====================
echo -e "${YELLOW}[2/6] 拉取最新代码...${NC}"
cd "$PROJECT_DIR"

if [ -d ".git" ]; then
    echo "当前分支: $(git branch --show-current)"
    git pull origin main
    echo -e "${GREEN}✅ 代码更新完成${NC}"
else
    echo -e "${YELLOW}⚠️  非 Git 仓库，跳过拉取${NC}"
fi

# ==================== 步骤 3: 激活虚拟环境 ====================
echo -e "${YELLOW}[3/6] 激活虚拟环境...${NC}"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ 未找到虚拟环境，请先创建：python -m venv venv${NC}"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✅ 虚拟环境已激活${NC}"

# ==================== 步骤 4: 运行数据库迁移 ====================
echo -e "${YELLOW}[4/6] 运行数据库迁移...${NC}"

if [ ! -f "migrations/add_folders_and_folder_id.py" ]; then
    echo -e "${RED}❌ 未找到迁移脚本${NC}"
    exit 1
fi

python migrations/add_folders_and_folder_id.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库迁移成功${NC}"
else
    echo -e "${RED}❌ 数据库迁移失败${NC}"
    echo "正在恢复备份..."
    if [ -f "$BACKUP_FILE" ]; then
        cp "$BACKUP_FILE" cshine.db
        echo -e "${GREEN}✅ 已恢复到备份版本${NC}"
    fi
    exit 1
fi

# ==================== 步骤 5: 重启服务 ====================
echo -e "${YELLOW}[5/6] 重启后端服务...${NC}"

# 检测服务管理方式
if command -v systemctl &> /dev/null && systemctl is-active --quiet cshine; then
    echo "使用 systemd 重启服务..."
    sudo systemctl restart cshine
    sleep 2
    sudo systemctl status cshine --no-pager
    
elif [ -f "server.pid" ]; then
    echo "使用 PID 文件重启服务..."
    OLD_PID=$(cat server.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "停止旧进程 (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    
    echo "启动新进程..."
    nohup python main.py > server.log 2>&1 &
    NEW_PID=$!
    echo $NEW_PID > server.pid
    echo -e "${GREEN}✅ 服务已启动 (PID: $NEW_PID)${NC}"
    
else
    echo "未检测到运行中的服务，启动新服务..."
    nohup python main.py > server.log 2>&1 &
    echo $! > server.pid
    echo -e "${GREEN}✅ 服务已启动 (PID: $(cat server.pid))${NC}"
fi

# 等待服务启动
echo "等待服务启动..."
sleep 3

# ==================== 步骤 6: 验证部署 ====================
echo -e "${YELLOW}[6/6] 验证部署结果...${NC}"

# 检查健康状态
HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")

if echo "$HEALTH_CHECK" | grep -q "healthy"; then
    echo -e "${GREEN}✅ 服务健康检查通过${NC}"
    
    # 检查 API 文档
    DOCS_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs 2>/dev/null || echo "000")
    if [ "$DOCS_CHECK" = "200" ]; then
        echo -e "${GREEN}✅ API 文档可访问${NC}"
    else
        echo -e "${YELLOW}⚠️  API 文档访问异常 (状态码: $DOCS_CHECK)${NC}"
    fi
    
    # 显示部署信息
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          🎉 部署成功！                     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📝 新增功能:${NC}"
    echo "  • 文件上传功能（支持 mp3/m4a/wav）"
    echo "  • 知识库管理（创建、查询、更新、删除）"
    echo "  • 会议按知识库筛选"
    echo ""
    echo -e "${BLUE}🌐 服务信息:${NC}"
    echo "  • 服务地址: http://localhost:8000"
    echo "  • API 文档: http://localhost:8000/docs"
    echo "  • 健康检查: http://localhost:8000/health"
    echo ""
    echo -e "${BLUE}📋 新增 API 端点:${NC}"
    echo "  • GET  /api/v1/upload/oss-signature  - OSS 上传签名"
    echo "  • POST /api/v1/folders              - 创建知识库"
    echo "  • GET  /api/v1/folders              - 获取知识库列表"
    echo "  • GET  /api/v1/folders/{id}         - 获取知识库详情"
    echo "  • PUT  /api/v1/folders/{id}         - 更新知识库"
    echo "  • DELETE /api/v1/folders/{id}       - 删除知识库"
    echo ""
    echo -e "${BLUE}📊 数据库变更:${NC}"
    echo "  • 新增 folders 表（知识库）"
    echo "  • meetings 表新增 folder_id 字段"
    echo ""
    echo -e "${BLUE}📝 下一步:${NC}"
    echo "  1. 在微信开发者工具中编译小程序"
    echo "  2. 真机测试上传和知识库功能"
    echo "  3. 确认无误后上传代码（版本: v1.1.0）"
    echo "  4. 提交审核"
    echo ""
    echo -e "${YELLOW}💾 数据库备份位置: $BACKUP_FILE${NC}"
    echo ""
    
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    echo ""
    echo "查看最近的日志:"
    tail -20 logs/cshine.log 2>/dev/null || tail -20 server.log
    echo ""
    echo -e "${YELLOW}建议操作:${NC}"
    echo "  1. 查看完整日志: tail -50 $BACKEND_DIR/logs/cshine.log"
    echo "  2. 检查端口占用: lsof -i :8000"
    echo "  3. 手动启动调试: cd $BACKEND_DIR && source venv/bin/activate && python main.py"
    echo ""
    exit 1
fi

# ==================== 清理 ====================
deactivate 2>/dev/null || true

echo -e "${GREEN}部署流程完成！${NC}"

