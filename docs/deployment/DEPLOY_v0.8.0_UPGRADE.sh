#!/bin/bash
# ============================================
# Cshine 升级脚本：v0.6.2 → v0.8.1
# ============================================
# 日期: 2025-11-13
# 更新内容:
#   - v0.7.0: AI 调用逻辑重构
#   - v0.8.0: Web 管理后台
#   - v0.8.1: 文档更新
# ============================================

set -e  # 遇到错误立即退出

echo "========================================"
echo "🚀 Cshine 升级：v0.6.2 → v0.8.1"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="/home/cshine/Cshine"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 1. 检查当前目录
echo "📍 检查当前位置..."
cd "$PROJECT_ROOT" || { echo "❌ 项目目录不存在"; exit 1; }
echo "   当前目录: $(pwd)"
echo ""

# 2. 检查当前分支和版本
echo "📊 检查当前版本..."
current_branch=$(git branch --show-current)
echo "   当前分支: $current_branch"
git log --oneline -1
echo ""

# 3. 备份当前状态
echo "💾 备份当前状态..."
backup_tag="backup_before_v0.8.0_$(date +%Y%m%d_%H%M%S)"
git tag "$backup_tag"
echo -e "   ${GREEN}✅ 创建备份标签: $backup_tag${NC}"
echo ""

# 4. 拉取最新代码
echo "⬇️  拉取最新代码..."
git fetch origin
git pull origin main
echo -e "   ${GREEN}✅ 代码更新完成${NC}"
echo ""

# 5. 显示更新内容
echo "📝 更新内容概览..."
echo ""
echo "   v0.7.0 - AI 调用逻辑重构"
echo "   ✨ LLM 分类器（智能分类、关键词提取）"
echo "   ✨ 闪记和会议处理支持 AI 模型选择"
echo "   ✨ 自动降级机制（LLM 失败→规则分类器）"
echo ""
echo "   v0.8.0 - Web 管理后台"
echo "   ✨ AI 模型可视化管理"
echo "   ✨ 提示词模板查看"
echo "   ✨ 现代化的 Bootstrap UI"
echo ""

# 6. 检查数据库连接（可选）
echo "🗄️  检查数据库连接..."
if psql -h localhost -U cshine_user -d cshine -c '\q' 2>/dev/null; then
    echo -e "   ${GREEN}✅ 数据库连接正常${NC}"
else
    echo -e "   ${YELLOW}⚠️  无法连接数据库（需要输入密码时属正常）${NC}"
fi
echo ""

# 7. 检查静态文件
echo "📁 检查静态文件..."
if [ -d "$BACKEND_DIR/static/admin" ]; then
    echo -e "   ${GREEN}✅ Web 管理后台文件存在${NC}"
    ls -lh "$BACKEND_DIR/static/admin/"
else
    echo -e "   ${RED}❌ 静态文件目录不存在${NC}"
    exit 1
fi
echo ""

# 8. 重启服务
echo "🔄 重启服务..."
echo "   停止服务..."
sudo systemctl stop cshine-api

echo "   等待 3 秒..."
sleep 3

echo "   启动服务..."
sudo systemctl start cshine-api

echo "   等待服务启动..."
sleep 5
echo ""

# 9. 检查服务状态
echo "✅ 验证服务状态..."
if sudo systemctl is-active --quiet cshine-api; then
    echo -e "   ${GREEN}✅ 服务运行正常${NC}"
    sudo systemctl status cshine-api --no-pager -l | head -n 15
else
    echo -e "   ${RED}❌ 服务启动失败${NC}"
    echo "   查看日志："
    sudo journalctl -u cshine-api -n 30
    exit 1
fi
echo ""

# 10. 测试 API 接口
echo "🧪 测试 API 接口..."

# 测试健康检查
echo -n "   测试健康检查: "
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 测试 HTTPS 健康检查
echo -n "   测试 HTTPS 健康检查: "
if curl -s https://cshine.xuyucloud.com/health | grep -q "healthy"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 测试管理后台静态文件
echo -n "   测试 Web 管理后台: "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/static/admin/login.html | grep -q "200"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 测试 HTTPS 管理后台
echo -n "   测试 HTTPS 管理后台: "
if curl -s -o /dev/null -w "%{http_code}" https://cshine.xuyucloud.com/static/admin/login.html | grep -q "200"; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
fi

# 测试管理员登录 API
echo -n "   测试管理员登录 API: "
login_response=$(curl -s -X POST http://localhost:8000/api/v1/api/admin/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123456"}')
if echo "$login_response" | grep -q '"code":200'; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${RED}❌${NC}"
    echo "   响应: $login_response"
fi

echo ""

# 11. 显示访问信息
echo "========================================"
echo "🎉 升级完成！"
echo "========================================"
echo ""
echo "📍 访问地址："
echo "   Web 管理后台: https://cshine.xuyucloud.com/static/admin/login.html"
echo "   默认账号: admin / admin123456"
echo ""
echo "⚠️  重要提醒："
echo "   1. 首次登录后请立即修改默认密码"
echo "   2. 建议限制管理后台的访问 IP"
echo "   3. 确保使用 HTTPS 访问"
echo ""
echo "📚 相关文档："
echo "   部署文档: $PROJECT_ROOT/docs/features/DEPLOY_WEB_ADMIN_20251113.md"
echo "   使用指南: $PROJECT_ROOT/backend/static/admin/README.md"
echo ""
echo "🔍 查看日志："
echo "   实时日志: sudo journalctl -u cshine-api -f"
echo "   最近日志: sudo journalctl -u cshine-api -n 50"
echo ""
echo "🔙 如需回滚："
echo "   git reset --hard $backup_tag"
echo "   sudo systemctl restart cshine-api"
echo ""
echo "========================================"

