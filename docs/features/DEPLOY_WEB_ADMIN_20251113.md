# Web 管理后台部署文档

**版本**: v0.8.0  
**日期**: 2025-11-13  
**作者**: AI Assistant  
**状态**: ✅ 已完成

---

## 📋 更新概览

### 更新类型
**新功能** - Web 管理后台界面

### 是否必须
**建议🟡** - 提供可视化管理界面，大幅提升管理效率

### 预计停机时间
**无** - 仅需重启服务（<5分钟）

---

## 🎯 功能说明

### 核心功能

#### 1. Web 管理后台界面
- 🎨 现代化的 Bootstrap 5 UI
- 📱 响应式设计，支持移动端
- 🔐 JWT Token 安全认证
- 🚀 单页应用（SPA）体验

#### 2. AI 模型管理
- ➕ 添加新的 AI 模型
- ✏️ 编辑现有模型配置
- 🗑️ 删除不需要的模型
- 🔬 测试模型连接
- ⭐ 设置默认模型
- 🔄 启用/禁用模型

#### 3. 提示词管理
- 👀 查看系统预置模板
- 📂 按场景分类展示
- 📝 查看模板详细内容

---

## 📦 涉及文件

### 新增文件
```
backend/static/admin/
├── login.html          # 登录页面
├── index.html          # 主管理页面
├── app.js              # 前端业务逻辑
└── README.md           # 使用文档
```

### 修改文件
```
backend/main.py         # 添加静态文件服务
docs/core/CHANGELOG.md  # 更新日志
```

---

## 🗄️ 数据库变更

**无数据库变更** - 使用现有的 `admin_users`、`ai_models`、`ai_prompts` 表

---

## 🔧 依赖变更

**无新增依赖** - 使用 FastAPI 内置的 `StaticFiles`

---

## 🌐 环境变量变更

**无新增环境变量**

---

## 📥 部署步骤

### 方式1：自动脚本（推荐）✅

```bash
# 在服务器上执行
bash docs/deployment/UPDATE_SERVER.sh
```

### 方式2：手动步骤

#### 步骤 1：拉取最新代码

```bash
cd /home/cshine/Cshine
git pull origin main
```

#### 步骤 2：重启服务

```bash
sudo systemctl restart cshine-api
```

#### 步骤 3：验证服务

```bash
# 1. 检查服务状态
sudo systemctl status cshine-api

# 2. 测试 API
curl http://localhost:8000/health

# 3. 测试静态文件（本地）
curl -I http://localhost:8000/static/admin/login.html

# 4. 测试静态文件（生产）
curl -I https://cshine.xuyucloud.com/static/admin/login.html
```

---

## ✅ 验证方法

### 1. 访问管理后台

**生产环境**：
```
https://cshine.xuyucloud.com/static/admin/login.html
```

**本地环境**：
```
http://localhost:8000/static/admin/login.html
```

### 2. 登录测试

**默认账号**：
- 用户名：`admin`
- 密码：`admin123456`

**⚠️ 重要**：首次登录后，请立即修改默认密码！

### 3. 功能测试

#### 测试 AI 模型管理
1. 点击「添加模型」
2. 填写测试模型信息（可以用假的 API Key）
3. 保存后查看模型列表
4. 尝试编辑模型
5. 尝试删除模型

#### 测试提示词管理
1. 切换到「提示词管理」页面
2. 查看默认的 4 个提示词模板
3. 点击「查看」查看模板详情

### 4. 验证命令

```bash
# 测试管理后台静态文件
curl -I https://cshine.xuyucloud.com/static/admin/login.html

# 测试管理员登录 API
curl -X POST https://cshine.xuyucloud.com/api/v1/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'

# 预期返回：
# {"code":200,"message":"登录成功","data":{"token":"...","admin_id":"...","username":"admin","is_superuser":true}}
```

---

## 🔙 回滚方案

如果更新后出现问题，按以下步骤回滚：

### 1. 回滚代码

```bash
cd /home/cshine/Cshine
git reset --hard HEAD~1
git log --oneline -5  # 确认回滚成功
```

### 2. 重启服务

```bash
sudo systemctl restart cshine-api
```

### 3. 验证

```bash
curl http://localhost:8000/health
```

---

## 🔐 安全配置（重要）

### 1. 修改默认密码

首次部署后，**必须**修改默认管理员密码：

#### 方法 1：使用 Python 脚本

```python
# 在服务器上执行
cd /home/cshine/Cshine/backend

python3.11 << EOF
import bcrypt
from app.database import SessionLocal
from app.models import AdminUser

# 生成新密码哈希
new_password = "your_secure_password_here"  # 修改为你的新密码
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

#### 方法 2：直接操作数据库

```bash
# 1. 生成密码哈希
python3.11 << EOF
import bcrypt
password = "your_secure_password_here"
hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(hash)
EOF

# 2. 更新数据库（复制上面输出的哈希值）
psql -h localhost -U cshine_user -d cshine
UPDATE admin_users 
SET password_hash = '$2b$12$your_hash_here' 
WHERE username = 'admin';
\q
```

### 2. 配置访问限制（可选）

#### 使用 Nginx 限制 IP

编辑 `/etc/nginx/sites-available/cshine.conf`：

```nginx
# 管理后台路径
location /static/admin/ {
    # 只允许特定 IP 访问
    allow 123.45.67.89;    # 你的 IP
    allow 10.0.0.0/8;      # 内网 IP
    deny all;              # 拒绝其他所有 IP
    
    # 代理到后端
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

重启 Nginx：

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 启用 HTTPS（必须）

生产环境**必须**使用 HTTPS 访问管理后台。

检查 HTTPS 配置：

```bash
# 访问管理后台应该自动跳转到 HTTPS
curl -I http://cshine.xuyucloud.com/static/admin/login.html

# 应该返回 301 或 308 重定向
```

---

## 📖 使用指南

### 添加 AI 模型

1. 登录管理后台
2. 确保在「AI 模型管理」页面
3. 点击右上角「添加模型」按钮
4. 填写模型信息：
   - **模型名称**：自定义名称，例如 "GPT-4 Turbo"
   - **提供商**：选择 OpenAI / Anthropic / 豆包 / 通义
   - **模型 ID**：模型的实际标识符，例如 "gpt-4-turbo-preview"
   - **API Key**：从提供商获取的密钥
   - **API Base URL**：可选，自定义端点
   - **最大 Token**：单次请求的 token 上限
   - **温度**：0-100，控制输出随机性
   - **描述**：备注信息
5. 勾选「启用此模型」
6. （可选）勾选「设为默认模型」
7. 点击「保存」
8. 点击「测试」验证配置是否正确

### 小程序端使用

添加模型后，用户在小程序中：
- 创建会议记录时可以选择使用的 AI 模型
- 创建闪记时可以选择使用的 AI 模型
- 不选择时使用默认模型或规则分类器

---

## 🐛 故障排除

### 1. 无法访问管理后台

**症状**：访问 `/static/admin/login.html` 返回 404

**排查步骤**：

```bash
# 1. 检查服务是否运行
sudo systemctl status cshine-api

# 2. 检查静态文件是否存在
ls -la /home/cshine/Cshine/backend/static/admin/

# 3. 检查服务日志
sudo journalctl -u cshine-api -n 50

# 4. 测试本地访问
curl -I http://localhost:8000/static/admin/login.html
```

**解决方案**：

```bash
# 重新拉取代码
cd /home/cshine/Cshine
git pull origin main

# 确认静态文件存在
ls -la backend/static/admin/

# 重启服务
sudo systemctl restart cshine-api
```

### 2. 登录失败

**症状**：输入正确的用户名密码，但显示「登录失败」

**排查步骤**：

```bash
# 1. 测试登录 API
curl -X POST http://localhost:8000/api/v1/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123456"}'

# 2. 检查数据库
cd /home/cshine/Cshine/backend
python3.11 << EOF
from app.database import SessionLocal
from app.models import AdminUser

db = SessionLocal()
admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
if admin:
    print(f"✅ 管理员账号存在: {admin.username}")
    print(f"   ID: {admin.id}")
    print(f"   超级用户: {admin.is_superuser}")
else:
    print("❌ 管理员账号不存在")
db.close()
EOF
```

**解决方案**：

如果管理员账号不存在，运行初始化脚本：

```bash
cd /home/cshine/Cshine/backend
python3.11 init_ai_system.py
```

### 3. 页面加载缓慢

**原因**：CDN 资源加载慢

**解决方案**：

1. 检查网络连接
2. 考虑使用国内 CDN
3. 或者下载静态资源到本地

### 4. 模型测试失败

**可能原因**：
- API Key 错误
- 网络连接问题
- 模型 ID 不存在
- API Base URL 配置错误

**排查**：

```bash
# 查看服务日志
sudo journalctl -u cshine-api -f

# 测试网络连接
curl https://api.openai.com/v1/models
```

---

## 📊 性能影响

- **CPU**: 无明显影响（静态文件服务开销很小）
- **内存**: 无明显影响
- **磁盘**: 新增约 50KB 静态文件
- **网络**: 首次访问需要加载 CDN 资源（Bootstrap、Font Awesome）

---

## 🔄 兼容性

### 向后兼容
- ✅ 完全兼容现有 API
- ✅ 不影响小程序端功能
- ✅ 不影响现有数据

### 浏览器兼容性
- ✅ Chrome / Edge（推荐）
- ✅ Firefox
- ✅ Safari
- ❌ IE（不支持）

---

## 📚 相关文档

- [Web 管理后台使用说明](../../backend/static/admin/README.md)
- [AI 模型管理系统部署文档](DEPLOY_AI_MODELS_SYSTEM_20251113.md)
- [后端更新协议](../deployment/BACKEND_UPDATE_PROTOCOL.md)
- [开发指南](../core/DEVELOPMENT_GUIDE.md)

---

## 📞 技术支持

如有问题，请：
1. 查看 [故障排除](#-故障排除) 章节
2. 检查服务日志：`sudo journalctl -u cshine-api -n 100`
3. 查看应用日志：`tail -f /home/cshine/Cshine/backend/logs/cshine.log`

---

**Let Your Ideas Shine. ✨**

