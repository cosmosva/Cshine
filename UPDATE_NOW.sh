#!/bin/bash
# Cshine 后端快速更新脚本
# 使用方法：bash UPDATE_NOW.sh

echo "🚀 开始更新线上后端..."
echo ""

# 替换为你的服务器地址
SERVER_USER="cshine"
SERVER_HOST="your-server-ip-or-domain"

echo "📝 更新步骤："
echo "1. 拉取最新代码"
echo "2. 更新依赖"
echo "3. 重启服务"
echo "4. 健康检查"
echo ""

read -p "服务器地址 (默认: $SERVER_USER@$SERVER_HOST): " input_server
if [ -n "$input_server" ]; then
    SERVER_ADDR="$input_server"
else
    SERVER_ADDR="$SERVER_USER@$SERVER_HOST"
fi

echo ""
echo "🔗 连接服务器: $SERVER_ADDR"
echo ""

ssh "$SERVER_ADDR" << 'ENDSSH'
    set -e
    
    echo "📦 1/4: 进入项目目录..."
    cd ~/Cshine
    
    echo "📦 2/4: 拉取最新代码..."
    git pull origin main
    
    echo "📦 3/4: 更新后端服务..."
    cd backend
    source venv/bin/activate
    pip install -r requirements.txt --quiet
    
    echo "📦 4/4: 重启服务..."
    sudo systemctl restart cshine-api
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet cshine-api; then
        echo ""
        echo "✅ 服务启动成功！"
        echo ""
        
        # 健康检查
        echo "🔍 健康检查..."
        curl -s http://127.0.0.1:8000/health || echo "无法连接健康检查接口"
        echo ""
        
        # 检查配置
        echo "🔍 配置检查..."
        python -c "
from config import settings
print(f'AppID: {settings.WECHAT_APPID}')
print(f'Secret: {\"已配置\" if settings.WECHAT_SECRET else \"未配置\"}')
print(f'OSS: {settings.OSS_BUCKET_NAME}')
"
        echo ""
        echo "🎉 更新完成！"
        
    else
        echo ""
        echo "❌ 服务启动失败！"
        echo ""
        echo "📋 查看错误日志："
        sudo journalctl -u cshine-api -n 30 --no-pager
        exit 1
    fi
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 线上后端更新成功！"
    echo "=========================================="
    echo ""
    echo "📱 现在可以测试小程序登录功能了"
else
    echo ""
    echo "=========================================="
    echo "  ❌ 更新失败"
    echo "=========================================="
    echo ""
    echo "💡 请检查："
    echo "   1. 服务器地址是否正确"
    echo "   2. SSH 连接是否正常"
    echo "   3. 查看上面的错误信息"
fi

