#!/bin/bash
# Systemd 服务配置脚本

if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

echo "配置 Systemd 服务..."

# 创建服务文件
cat > /etc/systemd/system/cshine-api.service << 'EOF'
[Unit]
Description=Cshine FastAPI Application
After=network.target postgresql.service

[Service]
Type=notify
User=cshine
Group=cshine
WorkingDirectory=/home/cshine/Cshine/backend
Environment="PATH=/home/cshine/Cshine/backend/venv/bin"
ExecStart=/home/cshine/Cshine/backend/venv/bin/uvicorn main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log \
    --use-colors

# 重启策略
Restart=always
RestartSec=10

# 安全配置
NoNewPrivileges=true
PrivateTmp=true

# 日志
StandardOutput=append:/home/cshine/Cshine/backend/logs/uvicorn.log
StandardError=append:/home/cshine/Cshine/backend/logs/uvicorn.error.log

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
systemctl daemon-reload

# 启动服务
systemctl start cshine-api

# 设置开机自启
systemctl enable cshine-api

echo "✅ Systemd 服务配置完成"
echo ""
echo "服务状态："
systemctl status cshine-api --no-pager

