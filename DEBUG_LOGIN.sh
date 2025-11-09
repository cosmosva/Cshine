#!/bin/bash
# 诊断登录问题
# 服务器: cshine@8.134.254.88

echo "=========================================="
echo "  🔍 诊断 Cshine 登录问题"
echo "=========================================="
echo ""

ssh cshine@8.134.254.88 << 'ENDSSH'
    echo "📦 1. 检查代码版本"
    echo "=========================================="
    cd ~/Cshine
    echo "当前版本: $(git log --oneline -1)"
    echo ""
    
    echo "📦 2. 检查服务状态"
    echo "=========================================="
    if systemctl is-active --quiet cshine-api 2>/dev/null; then
        echo "✅ systemd 服务: active (running)"
        systemctl status cshine-api --no-pager | head -10
    elif pgrep -f "python.*main.py" > /dev/null; then
        echo "✅ Python 进程正在运行:"
        ps aux | grep "[p]ython.*main.py"
    else
        echo "❌ 服务未运行！"
    fi
    echo ""
    
    echo "📦 3. 检查健康接口"
    echo "=========================================="
    HEALTH=$(curl -s http://127.0.0.1:8000/health 2>/dev/null || echo "")
    if [ -n "$HEALTH" ]; then
        echo "✅ 健康检查: $HEALTH"
    else
        echo "❌ 健康检查失败：无法连接到服务"
    fi
    echo ""
    
    echo "📦 4. 检查配置文件"
    echo "=========================================="
    cd ~/Cshine/backend
    if [ -f .env ]; then
        echo "✅ .env 文件存在"
        echo ""
        echo "微信配置:"
        grep "WECHAT_APPID" .env || echo "❌ 缺少 WECHAT_APPID"
        grep "WECHAT_SECRET" .env | sed 's/=.*/=***hidden***/' || echo "❌ 缺少 WECHAT_SECRET"
        echo ""
        echo "OSS 配置:"
        grep "OSS_BUCKET_NAME" .env || echo "⚠️  未配置 OSS_BUCKET_NAME"
        grep "STORAGE_TYPE" .env || echo "⚠️  未配置 STORAGE_TYPE"
    else
        echo "❌ .env 文件不存在！"
    fi
    echo ""
    
    echo "📦 5. 测试登录接口"
    echo "=========================================="
    LOGIN_RESP=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"code":"test123"}' 2>/dev/null || echo "")
    
    if [ -n "$LOGIN_RESP" ]; then
        echo "接口响应: $LOGIN_RESP"
        if echo "$LOGIN_RESP" | grep -q "invalid code\|微信登录失败"; then
            echo "✅ 接口正常（code 无效是预期的）"
        elif echo "$LOGIN_RESP" | grep -q "WECHAT_APPID\|WECHAT_SECRET"; then
            echo "❌ 配置错误：微信 AppID/Secret 未配置"
        else
            echo "⚠️  未知响应"
        fi
    else
        echo "❌ 接口无响应"
    fi
    echo ""
    
    echo "📦 6. 检查日志（最近 20 行）"
    echo "=========================================="
    if [ -f ~/Cshine/backend/logs/cshine.log ]; then
        echo "应用日志:"
        tail -n 20 ~/Cshine/backend/logs/cshine.log
    else
        echo "⚠️  未找到应用日志"
    fi
    echo ""
    
    echo "systemd 日志（如果有）:"
    sudo journalctl -u cshine-api -n 20 --no-pager 2>/dev/null || echo "无法读取 systemd 日志（需要 sudo）"
    echo ""
    
    echo "📦 7. Python 配置验证"
    echo "=========================================="
    cd ~/Cshine/backend
    source venv/bin/activate
    python -c "
try:
    from config import settings
    print('✅ 配置加载成功')
    print(f'   AppID: {settings.WECHAT_APPID if settings.WECHAT_APPID else \"❌ 未配置\"}')
    print(f'   Secret: {\"✅ 已配置\" if settings.WECHAT_SECRET else \"❌ 未配置\"}')
    print(f'   OSS Bucket: {settings.OSS_BUCKET_NAME}')
except Exception as e:
    print(f'❌ 配置加载失败: {e}')
"
    echo ""
    
ENDSSH

echo ""
echo "=========================================="
echo "  📊 诊断完成"
echo "=========================================="
echo ""
echo "📱 如果服务正常，检查小程序端："
echo "   1. 微信开发者工具 → 清除缓存"
echo "   2. 重新编译"
echo "   3. 查看控制台错误信息"
echo ""

