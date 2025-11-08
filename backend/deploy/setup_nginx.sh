#!/bin/bash
# Nginx 配置脚本

if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

echo "=========================================="
echo "  Nginx 配置"
echo "=========================================="
echo ""

# 输入域名
read -p "请输入 API 域名 (如: api.cshine.com): " API_DOMAIN

if [ -z "$API_DOMAIN" ]; then
    echo "❌ 域名不能为空"
    exit 1
fi

echo ""
echo "配置 Nginx for $API_DOMAIN ..."

# 创建配置文件
cat > /etc/nginx/sites-available/cshine << EOF
# Upstream 配置
upstream cshine_api {
    server 127.0.0.1:8000;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${API_DOMAIN};

    # Let's Encrypt 验证
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # 其他请求重定向到 HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${API_DOMAIN};

    # SSL 证书配置（Let's Encrypt 会自动填充）
    ssl_certificate /etc/letsencrypt/live/${API_DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${API_DOMAIN}/privkey.pem;

    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # 客户端上传大小限制
    client_max_body_size 500M;

    # 超时配置
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;

    # 日志
    access_log /var/log/nginx/cshine_access.log;
    error_log /var/log/nginx/cshine_error.log;

    # API 请求代理
    location / {
        proxy_pass http://cshine_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件
    location /static/ {
        alias /home/cshine/Cshine/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 上传文件
    location /uploads/ {
        alias /home/cshine/Cshine/backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        proxy_pass http://cshine_api/health;
        access_log off;
    }
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/cshine /etc/nginx/sites-enabled/

# 删除默认配置
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置成功"
    
    # 重载 Nginx
    systemctl reload nginx
    
    echo ""
    echo "=========================================="
    echo "  🎉 Nginx 配置完成！"
    echo "=========================================="
    echo ""
    echo "📋 下一步："
    echo "1. 确保域名已解析到服务器 IP"
    echo "2. 申请 SSL 证书："
    echo "   sudo certbot --nginx -d ${API_DOMAIN}"
    echo ""
    echo "3. 测试访问："
    echo "   curl http://${API_DOMAIN}/health"
    echo ""
else
    echo "❌ Nginx 配置测试失败，请检查配置"
    exit 1
fi

