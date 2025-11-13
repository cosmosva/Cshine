# 🚀 线上升级指南：v0.6.2 → v0.8.1

**更新时间**: 2025-11-13  
**预计停机时间**: < 5 分钟  
**数据库变更**: 无

---

## 📋 更新内容

### v0.7.0 - AI 调用逻辑重构
- ✅ LLM 分类器（智能分类、关键词提取）
- ✅ 闪记和会议处理支持 AI 模型选择
- ✅ 自动降级机制

### v0.8.0 - Web 管理后台
- ✅ AI 模型可视化管理界面
- ✅ 提示词模板查看
- ✅ 现代化的 Bootstrap UI
- ✅ JWT 认证登录

### v0.8.1 - 文档更新
- ✅ Web 管理后台部署文档

---

## ⚡ 快速部署（推荐）

### 方式 1：自动脚本

```bash
# SSH 到服务器
ssh cshine@8.134.254.88

# 下载并执行升级脚本
cd /home/cshine/Cshine
git pull origin main
bash docs/deployment/DEPLOY_v0.8.0_UPGRADE.sh
```

脚本会自动完成：
- ✅ 创建备份标签
- ✅ 拉取最新代码
- ✅ 重启服务
- ✅ 运行测试验证

---

## 🔧 手动部署（详细步骤）

### 步骤 1：SSH 连接服务器

```bash
ssh cshine@8.134.254.88
```

### 步骤 2：创建备份

```bash
cd /home/cshine/Cshine

# 创建备份标签
git tag backup_before_v0.8.0_$(date +%Y%m%d_%H%M%S)

# 查看当前版本
git log --oneline -1
```

### 步骤 3：拉取最新代码

```bash
git pull origin main
```

### 步骤 4：检查静态文件

```bash
# 确认 Web 管理后台文件存在
ls -la backend/static/admin/

# 应该看到：
# - login.html
# - index.html
# - app.js
# - README.md
```

### 步骤 5：重启服务

```bash
# 停止服务
sudo systemctl stop cshine-api

# 等待几秒
sleep 3

# 启动服务
sudo systemctl start cshine-api

# 检查状态
sudo systemctl status cshine-api
```

### 步骤 6：验证部署

```bash
# 1. 测试健康检查
curl http://localhost:8000/health
# 预期输出: {"status":"healthy"}

# 2. 测试 HTTPS
curl https://cshine.xuyucloud.com/health
# 预期输出: {"status":"healthy"}

# 3. 测试 Web 管理后台（本地）
curl -I http://localhost:8000/static/admin/login.html
# 预期: HTTP/1.1 200 OK

# 4. 测试 HTTPS 管理后台
curl -I https://cshine.xuyucloud.com/static/admin/login.html
# 预期: HTTP/1.1 200 OK

# 5. 测试管理员登录 API
curl -X POST http://localhost:8000/api/v1/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'
# 预期: {"code":200,"message":"登录成功",...}
```

### 步骤 7：浏览器访问测试

打开浏览器访问：
```
https://cshine.xuyucloud.com/static/admin/login.html
```

使用默认账号登录：
- 用户名：`admin`
- 密码：`admin123456`

**⚠️ 重要：首次登录后请立即修改密码！**

---

## ✅ 验证清单

- [ ] 健康检查 API 正常
- [ ] HTTPS 访问正常
- [ ] Web 管理后台页面可访问
- [ ] 管理员登录成功
- [ ] 可以查看 AI 模型列表
- [ ] 可以查看提示词列表
- [ ] 小程序端功能正常

---

## 🔐 安全配置（必须）

### 1. 修改默认密码

首次登录后，立即修改密码：

```bash
cd /home/cshine/Cshine/backend

# 使用 Python 脚本修改
python3.11 << 'EOF'
import bcrypt
from app.database import SessionLocal
from app.models import AdminUser

# 设置新密码（请修改为你的密码）
new_password = "YOUR_SECURE_PASSWORD_HERE"
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 更新数据库
db = SessionLocal()
admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
if admin:
    admin.password_hash = password_hash
    db.commit()
    print("✅ 密码已更新")
else:
    print("❌ 管理员账号不存在")
db.close()
EOF
```

### 2. 配置 IP 访问限制（可选）

编辑 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/cshine.conf
```

添加：

```nginx
# 限制管理后台访问
location /static/admin/ {
    # 只允许你的 IP 访问
    allow YOUR_IP_ADDRESS;
    deny all;
    
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
}
```

重启 Nginx：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🐛 故障排除

### 问题 1：服务启动失败

**排查**：
```bash
# 查看服务状态
sudo systemctl status cshine-api

# 查看详细日志
sudo journalctl -u cshine-api -n 50

# 查看应用日志
tail -f /home/cshine/Cshine/backend/logs/cshine.log
```

**解决**：
```bash
# 检查是否有端口占用
sudo netstat -tlnp | grep 8000

# 尝试手动启动查看错误
cd /home/cshine/Cshine/backend
python3.11 -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 问题 2：管理后台 404

**排查**：
```bash
# 检查静态文件是否存在
ls -la /home/cshine/Cshine/backend/static/admin/

# 检查代码版本
cd /home/cshine/Cshine
git log --oneline -5
```

**解决**：
```bash
# 重新拉取代码
git pull origin main

# 重启服务
sudo systemctl restart cshine-api
```

### 问题 3：管理员登录失败

**排查**：
```bash
# 检查管理员账号
cd /home/cshine/Cshine/backend
python3.11 << 'EOF'
from app.database import SessionLocal
from app.models import AdminUser

db = SessionLocal()
admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
if admin:
    print(f"✅ 管理员存在: {admin.username}")
    print(f"   ID: {admin.id}")
    print(f"   超级用户: {admin.is_superuser}")
else:
    print("❌ 管理员账号不存在")
db.close()
EOF
```

**解决**：
如果账号不存在，重新运行初始化：
```bash
python3.11 init_ai_system.py
```

---

## 🔙 回滚方案

如果出现问题需要回滚：

```bash
cd /home/cshine/Cshine

# 查看备份标签
git tag | grep backup

# 回滚到备份版本
git reset --hard backup_before_v0.8.0_YYYYMMDD_HHMMSS

# 重启服务
sudo systemctl restart cshine-api

# 验证
curl http://localhost:8000/health
```

---

## 📱 小程序端测试

升级后，测试小程序功能是否正常：

1. 登录小程序
2. 创建闪记（测试语音转文字）
3. 创建会议记录（测试会议处理）
4. 查看知识库列表
5. 查看会议详情

**注意**：由于后端向后兼容，小程序端功能应该完全正常。

---

## 📞 支持

如有问题：

1. 查看日志：`sudo journalctl -u cshine-api -n 100`
2. 查看应用日志：`tail -f /home/cshine/Cshine/backend/logs/cshine.log`
3. 查看部署文档：`/home/cshine/Cshine/docs/features/DEPLOY_WEB_ADMIN_20251113.md`

---

## 🎯 下一步

部署完成后：

1. ✅ 修改默认管理员密码
2. ✅ 添加真实的 AI 模型（GPT-4、Claude 等）
3. ✅ 测试模型连接
4. ✅ 设置默认模型
5. ⏳ 等待小程序端添加模型选择功能

---

**Let Your Ideas Shine. ✨**

