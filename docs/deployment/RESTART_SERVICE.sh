#!/bin/bash
# 快速重启 Cshine 服务
# 使用方法: sudo bash docs/deployment/RESTART_SERVICE.sh

echo "=========================================="
echo "  🔄 重启 Cshine 服务"
echo "=========================================="
echo ""

# 检查服务状态
echo "📊 当前服务状态:"
systemctl status cshine-api --no-pager | head -5
echo ""

# 重启服务
echo "🔄 正在重启服务..."
systemctl restart cshine-api
sleep 3
echo ""

# 验证服务状态
echo "=========================================="
echo "  ✅ 验证服务状态"
echo "=========================================="
echo ""

if systemctl is-active --quiet cshine-api; then
    echo "✅ 服务运行正常"
    systemctl status cshine-api --no-pager | head -10
else
    echo "❌ 服务启动失败"
    echo ""
    echo "错误日志："
    journalctl -u cshine-api -n 30 --no-pager
    exit 1
fi

echo ""

# 健康检查
echo "🔍 健康检查..."
sleep 2
HEALTH=$(curl -s http://localhost:8000/health || echo "failed")
if [[ "$HEALTH" == *"healthy"* ]] || [[ "$HEALTH" == *"ok"* ]]; then
    echo "✅ 健康检查通过"
    echo "响应: $HEALTH"
else
    echo "❌ 健康检查失败"
    echo "响应: $HEALTH"
fi

echo ""
echo "=========================================="
echo "  ✅ 服务重启完成！"
echo "=========================================="
echo ""
echo "📝 后续操作："
echo "   1. 查看实时日志: journalctl -u cshine-api -f"
echo "   2. 测试小程序连接"
echo "   3. 测试上传功能"
echo ""

