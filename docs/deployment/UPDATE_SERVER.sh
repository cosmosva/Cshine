#!/bin/bash
# Cshine 服务器更新脚本
# 服务器: 8.134.254.88
# 用户: cshine
# 项目路径: ~/Cshine

echo "=========================================="
echo "  🚀 Cshine 服务器更新"
echo "  服务器: cshine@8.134.254.88"
echo "=========================================="
echo ""

echo "🔗 正在连接服务器..."
echo ""

ssh cshine@8.134.254.88 << 'ENDSSH'
    set -e
    
    echo "=========================================="
    echo "📦 步骤 1/6: 检查当前状态"
    echo "=========================================="
    cd ~/Cshine
    echo "✅ 当前分支: $(git branch --show-current)"
    echo "✅ 当前版本: $(git log --oneline -1)"
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 2/6: 备份数据库"
    echo "=========================================="
    cd backend
    if [ -f cshine.db ]; then
        BACKUP_FILE="cshine.db.backup.$(date +%Y%m%d_%H%M%S)"
        cp cshine.db "$BACKUP_FILE"
        echo "✅ 已备份到: $BACKUP_FILE"
    else
        echo "⚠️  未找到数据库文件"
    fi
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 3/6: 拉取最新代码"
    echo "=========================================="
    cd ~/Cshine
    
    # 显示更新前后的差异
    OLD_COMMIT=$(git log --oneline -1)
    git pull origin main
    NEW_COMMIT=$(git log --oneline -1)
    
    echo "✅ 代码更新完成"
    echo ""
    echo "更新内容："
    git log --oneline --graph -5
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 4/6: 检查配置"
    echo "=========================================="
    cd backend
    
    # 检查 .env 配置
    if [ ! -f .env ]; then
        echo "⚠️  警告: 未找到 .env 文件！"
        echo "请确保已配置以下环境变量："
        echo "  - WECHAT_APPID"
        echo "  - WECHAT_SECRET"
        echo "  - OSS_BUCKET_NAME=cshine-audio (生产环境)"
    else
        echo "✅ .env 文件存在"
        if grep -q "WECHAT_APPID=wx68cb1f3f6a2bcf17" .env; then
            echo "✅ 微信 AppID 已配置"
        else
            echo "⚠️  请检查微信 AppID 配置"
        fi
    fi
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 5/6: 执行数据库迁移"
    echo "=========================================="
    cd ~/Cshine
    
    # 激活虚拟环境（在项目根目录）
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ 虚拟环境已激活"
    else
        echo "⚠️  未找到虚拟环境，使用系统 Python"
    fi
    
    # 执行数据库迁移
    cd backend
    if [ -f "migrations/add_contacts_and_speakers.py" ]; then
        echo "正在执行数据库迁移..."
        python migrations/add_contacts_and_speakers.py
        echo "✅ 数据库迁移完成"
    else
        echo "⚠️  未找到迁移脚本，跳过迁移"
    fi
    
    # 检查依赖是否需要更新
    cd ~/Cshine/backend
    if git diff HEAD@{1} HEAD -- requirements.txt | grep -q "^+" 2>/dev/null; then
        echo "📦 检测到依赖变化，正在更新..."
        pip install -r requirements.txt --quiet
        echo "✅ 依赖更新完成"
    else
        echo "✅ 依赖无变化，跳过更新"
    fi
    echo ""
    
    echo "=========================================="
    echo "📦 步骤 6/6: 重启服务"
    echo "=========================================="
    sudo systemctl restart cshine-api
    
    echo "⏳ 等待服务启动..."
    sleep 3
    echo ""
    
    # 检查服务状态
    if systemctl is-active --quiet cshine-api; then
        echo "✅ 服务状态: active (running)"
    else
        echo "❌ 服务状态: inactive/failed"
        echo ""
        echo "错误日志："
        sudo journalctl -u cshine-api -n 30 --no-pager
        exit 1
    fi
    
    # 健康检查
    echo ""
    echo "🔍 健康检查..."
    sleep 2
    HEALTH_STATUS=$(curl -s http://127.0.0.1:8000/health || echo "")
    if echo "$HEALTH_STATUS" | grep -q "healthy\|ok"; then
        echo "✅ 健康检查: 通过"
        echo "响应: $HEALTH_STATUS"
    else
        echo "❌ 健康检查: 失败"
        echo "响应: $HEALTH_STATUS"
    fi
    
    # 数据库验证
    echo ""
    echo "🔍 数据库验证..."
    TABLE_COUNT=$(sudo -u postgres psql cshine_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('contacts', 'meeting_speakers');" 2>/dev/null || echo "0")
    if [ "$TABLE_COUNT" -eq 2 ]; then
        echo "✅ 新表已创建: contacts, meeting_speakers"
    else
        echo "⚠️  新表验证失败（找到 $TABLE_COUNT 个表）"
    fi
    
    COLUMN_COUNT=$(sudo -u postgres psql cshine_db -t -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'meetings' AND column_name = 'transcript_paragraphs';" 2>/dev/null || echo "0")
    if [ "$COLUMN_COUNT" -eq 1 ]; then
        echo "✅ 新字段已添加: transcript_paragraphs"
    else
        echo "⚠️  新字段验证失败"
    fi
    
    echo ""
    echo "=========================================="
    echo "  🎉 更新完成！"
    echo "=========================================="
    echo ""
    echo "📋 服务信息："
    sudo systemctl status cshine-api --no-pager | head -10
    
ENDSSH

UPDATE_STATUS=$?

echo ""
if [ $UPDATE_STATUS -eq 0 ]; then
    echo "=========================================="
    echo "  ✅ 服务器更新成功！"
    echo "=========================================="
    echo ""
    echo "🧪 在线验证："
    echo ""
    curl -s https://cshine.xuyucloud.com/health | python3 -m json.tool 2>/dev/null || \
    curl -s https://cshine.xuyucloud.com/health
    echo ""
    echo ""
    echo "📱 测试步骤："
    echo "   1. 清除小程序缓存"
    echo "   2. 重启小程序"
    echo "   3. 应该能自动登录成功"
    echo "   4. 进入'我的'页面，查看用户信息"
    echo "   5. 点击'完善资料'按钮测试授权"
    echo ""
else
    echo "=========================================="
    echo "  ❌ 更新失败"
    echo "=========================================="
    echo ""
    echo "🔧 故障排查："
    echo "   1. SSH 手动登录: ssh cshine@8.134.254.88"
    echo "   2. 查看日志: sudo journalctl -u cshine-api -n 50"
    echo "   3. 检查配置: cat ~/Cshine/backend/.env"
    echo ""
fi

