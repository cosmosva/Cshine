# 微信小程序配置指南

> 获取 AppID 和 AppSecret 的完整步骤

## 📋 前提条件

1. 已注册微信小程序账号
2. 已通过管理员身份认证

如果还没有小程序账号，请访问：https://mp.weixin.qq.com/

---

## 🔑 获取 AppID 和 AppSecret

### 步骤 1：登录微信公众平台

访问：https://mp.weixin.qq.com/

使用管理员微信扫码登录。

---

### 步骤 2：进入开发设置

1. 点击左侧菜单：**开发** → **开发管理**
2. 点击顶部 Tab：**开发设置**

---

### 步骤 3：复制 AppID

在"开发者ID"区域，你会看到：

```
AppID(小程序ID)：wx1234567890abcdef
```

点击右侧的 **复制** 按钮，保存 AppID。

---

### 步骤 4：获取 AppSecret

1. 在 AppSecret 区域，点击 **生成** 按钮（如果之前生成过，点击 **重置**）
2. **⚠️ 重要**：扫码后会显示 AppSecret，这是唯一一次显示机会
3. 立即复制并保存到安全的地方

**AppSecret 示例**：
```
1234567890abcdef1234567890abcdef
```

---

## ⚙️ 配置到项目

### 方法 1：使用环境变量（推荐）

1. 复制 `.env.example` 为 `.env`：
```bash
cd backend
cp .env.example .env
```

2. 编辑 `.env` 文件：
```bash
# 替换为你的真实值
WECHAT_APPID=wx1234567890abcdef
WECHAT_SECRET=1234567890abcdef1234567890abcdef
```

3. 重启后端服务

---

### 方法 2：直接修改配置文件（不推荐）

编辑 `backend/config.py`：

```python
WECHAT_APPID: str = "wx1234567890abcdef"
WECHAT_SECRET: str = "1234567890abcdef1234567890abcdef"
```

**⚠️ 注意**：不要将包含真实密钥的文件提交到 Git！

---

## ✅ 验证配置

### 1. 检查配置是否加载

启动后端服务，查看日志：

```bash
cd backend
python main.py
```

如果看到类似日志，说明配置成功：
```
INFO: 微信 AppID: wx1234******cdef (已配置)
```

### 2. 测试登录接口

使用 curl 测试（需要先从小程序获取 code）：

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "code": "微信登录code",
    "nickname": "测试用户",
    "avatar": ""
  }'
```

成功响应示例：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGc...",
    "user_id": "uuid...",
    "is_new_user": true
  }
}
```

---

## 🐛 常见问题

### Q1: 提示"Invalid WeChat code"

**原因**：
- AppID 或 AppSecret 配置错误
- code 已过期（code 只能使用一次，有效期 5 分钟）

**解决方法**：
1. 检查 `.env` 中的配置是否正确
2. 重新获取 code（小程序重新调用 `wx.login()`）
3. 确保 AppID 与小程序一致

---

### Q2: 提示"WECHAT_APPID not configured"

**原因**：环境变量未正确加载

**解决方法**：
1. 确认 `.env` 文件在 `backend/` 目录下
2. 检查 `.env` 格式是否正确（没有空格、引号）
3. 重启后端服务

---

### Q3: AppSecret 忘记了怎么办？

**解决方法**：
1. 回到微信公众平台
2. 开发 → 开发管理 → 开发设置
3. 点击 **重置** 按钮
4. 扫码后重新获取（会使旧的 Secret 失效）

---

### Q4: 可以公开 AppID 吗？

**AppID**：可以公开，不是敏感信息  
**AppSecret**：绝对不能公开！类似密码，必须保密

---

## 🔒 安全建议

1. ✅ **使用 .env 文件**
   - 不要将 .env 提交到 Git
   - 已在 .gitignore 中排除

2. ✅ **定期更换 AppSecret**
   - 建议每 3-6 个月更换一次
   - 团队成员离职时立即更换

3. ✅ **限制 IP 白名单**
   - 在微信公众平台设置服务器 IP 白名单
   - 只允许你的服务器 IP 调用微信 API

4. ✅ **监控异常调用**
   - 在微信公众平台查看 API 调用统计
   - 发现异常立即重置 Secret

---

## 📚 相关文档

- [微信小程序官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [微信登录接口文档](https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html)
- [Cshine 登录功能说明](../LOGIN_GUIDE.md)

---

## ✨ 配置完成后

恭喜！你已经完成微信小程序配置。

下一步：
1. 前往 [LOGIN_GUIDE.md](../LOGIN_GUIDE.md) 测试登录功能
2. 在小程序中测试登录流程
3. 查看后端日志验证登录成功

---

**配置有问题？** 请查看后端日志 `logs/cshine.log` 或提交 [Issue](https://github.com/cosmosva/Cshine/issues)

