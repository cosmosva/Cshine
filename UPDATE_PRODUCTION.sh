#!/bin/bash
# Cshine 生产环境快速更新脚本
# 域名: https://cshine.xuyucloud.com

set -e

echo "=========================================="
echo "  🚀 Cshine 生产环境更新"
echo "  域名: https://cshine.xuyucloud.com"
echo "=========================================="
echo ""

# 服务器配置（请根据实际情况修改）
SERVER_USER="${1:-cshine}"
SERVER_HOST="${2:-cshine.xuyucloud.com}"

echo "📝 更新信息："
echo "   服务器: $SERVER_USER@$SERVER_HOST"
echo "   目标: ~/Cshine"
echo ""

read -p "确认更新？(y/N): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""
echo "🔗 连接服务器并更新..."
echo ""

ssh "$SERVER_USER@$SERVER_HOST" << 'ENDSSH'
    set -e
    
    echo "=========================================="
    echo "📦 步骤 1/5: 检查当前状态"
    echo "=========================================="
    cd ~/Cshine
    echo "✅ 当前分支: $(git branch --show-current)"
    echo "✅ 最新提交: $(git log --oneline -1)"
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 2/5: 备份数据库"
    echo "=========================================="
    cd backend
    BACKUP_FILE="cshine.db.backup.$(date +%Y%m%d_%H%M%S)"
    if [ -f cshine.db ]; then
        cp cshine.db "$BACKUP_FILE"
        echo "✅ 已备份到: $BACKUP_FILE"
    else
        echo "⚠️  未找到数据库文件"
    fi
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 3/5: 拉取最新代码"
    echo "=========================================="
    cd ~/Cshine
    git pull origin main
    echo "✅ 代码更新完成"
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 4/5: 更新依赖并重启"
    echo "=========================================="
    cd backend
    source venv/bin/activate
    
    # 检查依赖是否需要更新
    if git diff HEAD@{1} HEAD -- requirements.txt | grep -q "^+"; then
        echo "📦 检测到依赖变化，正在更新..."
        pip install -r requirements.txt --quiet
        echo "✅ 依赖更新完成"
    else
        echo "✅ 依赖无变化"
    fi
    
    echo ""
    echo "🔄 重启服务..."
    sudo systemctl restart cshine-api
    
    # 等待服务启动
    sleep 3
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 5/5: 健康检查"
    echo "=========================================="
    
    # 检查服务状态
    if systemctl is-active --quiet cshine-api; then
        echo "✅ 服务状态: active (running)"
    else
        echo "❌ 服务状态: inactive"
        sudo systemctl status cshine-api --no-pager | head -10
        exit 1
    fi
    
    # 健康检查
    sleep 2
    HEALTH_STATUS=$(curl -s http://127.0.0.1:8000/health || echo "")
    if echo "$HEALTH_STATUS" | grep -q "healthy\|ok"; then
        echo "✅ 健康检查: 通过"
    else
        echo "❌ 健康检查: 失败"
        echo "响应: $HEALTH_STATUS"
    fi
    
    # 检查配置
    echo ""
    echo "🔍 配置检查:"
    python -c "
from config import settings
print(f'   AppID: {settings.WECHAT_APPID}')
print(f'   Secret: {\"✅ 已配置\" if settings.WECHAT_SECRET else \"❌ 未配置\"}')
print(f'   OSS Bucket: {settings.OSS_BUCKET_NAME}')
print(f'   Storage: {settings.STORAGE_TYPE}')
"
    
    echo ""
    echo "=========================================="
    echo "  🎉 更新完成！"
    echo "=========================================="
    echo ""
    echo "📋 最近更新："
    cd ~/Cshine
    git log --oneline -3
    
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 生产环境更新成功！"
    echo "=========================================="
    echo ""
    echo "🧪 在线验证："
    echo ""
    
    # 在线健康检查
    echo "🔍 健康检查..."
    curl -s https://cshine.xuyucloud.com/health | python3 -m json.tool 2>/dev/null || \
    curl -s https://cshine.xuyucloud.com/health
    
    echo ""
    echo ""
    echo "📱 现在可以测试小程序："
    echo "   1. 清除小程序缓存"
    echo "   2. 重启小程序"
    echo "   3. 应该能自动登录成功"
    echo "   4. 进入'我的'页面查看用户信息"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "  ❌ 更新失败"
    echo "=========================================="
    echo ""
    echo "💡 请检查上面的错误信息"
    echo ""
    echo "🔧 故障排查："
    echo "   ssh $SERVER_USER@$SERVER_HOST"
    echo "   sudo journalctl -u cshine-api -n 50"
    exit 1
fi

