# Cshine Web 管理后台

## 🎯 功能简介

轻量级的 Web 管理后台，用于管理 AI 模型和提示词模板。

### 核心功能
- 🤖 **AI 模型管理**
  - 添加、编辑、删除 AI 模型
  - 支持 OpenAI、Anthropic、字节豆包、阿里通义
  - 模型连接测试
  - 设置默认模型
  
- 📝 **提示词管理**
  - 查看系统预置的提示词模板
  - 支持会议摘要、闪记分类、行动项提取等场景

## 🚀 快速开始

### 访问地址

**本地开发**：
```
http://localhost:8000/static/admin/login.html
```

**生产环境**：
```
https://your-domain.com/static/admin/login.html
```

### 默认账号

```
用户名：admin
密码：admin123456
```

⚠️ **重要**：首次登录后，请立即在数据库中修改默认密码！

### 修改密码

连接数据库，执行：

```sql
-- 生成新的密码哈希（示例：新密码为 "your_new_password"）
-- 需要使用 bcrypt 工具生成哈希

UPDATE admin_users 
SET password_hash = '$2b$12$your_new_password_hash_here'
WHERE username = 'admin';
```

或使用 Python 脚本：

```python
import bcrypt

new_password = "your_new_password"
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"新密码哈希：{password_hash}")

# 将输出的哈希值更新到数据库中
```

## 📖 使用指南

### 1. AI 模型管理

#### 添加模型

1. 点击「添加模型」按钮
2. 填写以下信息：
   - **模型名称**：自定义名称（例如：GPT-4 Turbo）
   - **提供商**：选择模型提供商
   - **模型 ID**：模型的实际 ID（例如：gpt-4-turbo-preview）
   - **API Key**：从提供商获取的 API 密钥
   - **API Base URL**：可选，自定义 API 端点
   - **最大 Token**：单次请求的最大 token 数
   - **温度**：控制输出随机性（0-100）
   - **描述**：备注信息
3. 勾选「启用此模型」和「设为默认模型」（可选）
4. 点击「保存」

#### 编辑模型

1. 点击模型行的「编辑」按钮
2. 修改配置信息
3. 点击「保存」

**注意**：编辑时，如果不修改 API Key，请留空。

#### 测试模型

点击「测试」按钮，系统会向模型发送测试请求，验证配置是否正确。

#### 删除模型

点击「删除」按钮，确认后删除模型配置。

### 2. 提示词管理

当前版本支持查看系统预置的提示词模板，包括：

- **会议摘要生成**：从会议转录生成简洁摘要
- **闪记智能分类**：将闪记分类到工作、生活、学习等类别
- **行动项识别**：从内容中提取待办事项
- **关键要点提取**：提取3-5个关键信息点

点击「查看」可以查看模板的详细内容。

## 🔧 技术栈

- **前端**：HTML5 + Bootstrap 5 + Vanilla JavaScript
- **后端**：FastAPI + SQLAlchemy
- **认证**：JWT Token
- **数据库**：PostgreSQL / SQLite

## 🌐 浏览器兼容性

- Chrome / Edge：推荐
- Firefox：支持
- Safari：支持
- IE：不支持

## 📱 移动端

管理后台采用响应式设计，支持在移动设备上使用，但推荐使用桌面浏览器获得最佳体验。

## 🔐 安全建议

1. **修改默认密码**：首次部署后立即修改
2. **使用 HTTPS**：生产环境必须使用 HTTPS
3. **限制访问**：配置防火墙或 Nginx 限制访问 IP
4. **定期更新**：及时更新系统和依赖
5. **API Key 保护**：确保 API Key 的安全存储

## 🐛 故障排除

### 无法访问管理后台

**检查服务是否运行**：
```bash
curl http://localhost:8000/health
```

**检查静态文件目录**：
```bash
ls -la backend/static/admin/
```

### 登录失败

**检查管理员账号**：
```sql
SELECT * FROM admin_users WHERE username = 'admin';
```

**重置密码**：
```sql
-- 密码：admin123456
UPDATE admin_users 
SET password_hash = '$2b$12$5v8LIL7LGvBfMk3VYqFqaOYa3h7xHYN8EZGhQzFX.KJNzJYqKJYqK'
WHERE username = 'admin';
```

### 模型测试失败

1. 检查 API Key 是否正确
2. 检查网络连接
3. 检查模型 ID 是否存在
4. 查看服务器日志：`tail -f backend/logs/cshine.log`

## 📚 相关文档

- [AI 模型管理系统部署文档](../../docs/features/DEPLOY_AI_MODELS_SYSTEM_20251113.md)
- [后端更新协议](../../docs/deployment/BACKEND_UPDATE_PROTOCOL.md)
- [开发指南](../../docs/core/DEVELOPMENT_GUIDE.md)

## 🤝 贡献

欢迎提出改进建议和 Bug 报告！

---

**Let Your Ideas Shine. ✨**

