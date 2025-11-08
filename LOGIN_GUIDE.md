# Cshine 登录功能说明

> 最后更新：2025-11-08  
> 版本：v0.4.0

## 📋 概述

Cshine 使用微信小程序登录系统，支持两种登录方式：
1. **自动静默登录**：小程序启动时自动登录（不需要用户授权）
2. **完整授权登录**：用户在个人中心主动登录（获取昵称和头像）

## 🔐 登录流程

### 1. 自动静默登录（推荐）

**触发时机**：
- 用户首次打开小程序
- Token 失效或被清除后

**流程**：
```
小程序启动 (app.js onLaunch)
    ↓
检查本地 Token (checkLoginStatus)
    ↓
Token 不存在？
    ↓ 是
调用 wx.login() 获取 code
    ↓
调用后端 API /api/v1/auth/login
    ↓
保存 Token 和 user_id 到本地存储
    ↓
更新全局变量 globalData
    ↓
登录完成（用户无感知）
```

**优点**：
- ✅ 用户无感知，自动完成
- ✅ 无需弹窗授权
- ✅ 快速启动小程序

**缺点**：
- ⚠️ 无法获取用户昵称和头像（需要用户主动授权）

---

### 2. 完整授权登录

**触发时机**：
- 用户在"我的"页面点击"登录"按钮

**流程**：
```
用户点击"登录"按钮 (profile.js handleLogin)
    ↓
显示 Loading: "登录中..."
    ↓
调用 wx.login() 获取 code
    ↓
调用 wx.getUserProfile() 获取用户信息
    ↓ (需要用户授权)
用户授权成功
    ↓
调用后端 API /api/v1/auth/login
    ↓
保存 Token、user_id、nickname、avatar
    ↓
更新页面状态和统计数据
    ↓
显示 Toast: "登录成功" / "欢迎使用 Cshine！"
```

**优点**：
- ✅ 获取完整的用户信息（昵称、头像）
- ✅ 用户信息可用于显示和社交功能

**缺点**：
- ⚠️ 需要用户主动授权
- ⚠️ 用户可能拒绝授权

---

## 🔑 Token 管理

### 存储位置

使用 `wx.storage` 本地存储：

| Key | 说明 | 示例 |
|-----|------|------|
| `token` | JWT Token | `eyJhbGciOiJIUzI1...` |
| `userInfo` | 用户信息 | `{ id, nickname, avatar }` |

### Token 自动携带

所有需要认证的 API 请求会自动携带 Token：

```javascript
// utils/request.js
requestHeader['Authorization'] = `Bearer ${token}`
```

### Token 失效处理

当后端返回 `401 Unauthorized` 时：
1. 自动清除本地 Token 和用户信息
2. 显示提示："登录已过期，请重新登录"
3. 用户需要重新打开小程序（触发自动登录）或手动登录

---

## 👤 用户状态管理

### 全局变量 (app.js)

```javascript
globalData: {
  token: '',          // JWT Token
  userInfo: null,     // 用户信息对象
  userId: ''          // 用户ID
}
```

### 检查登录状态

在需要登录的页面中：

```javascript
const app = getApp()

// 方法1：检查是否已登录
if (app.checkLoginStatus()) {
  console.log('已登录')
}

// 方法2：确保已登录（未登录则自动登录）
await app.ensureLogin()
```

---

## 🧪 测试登录流程

### 1. 测试自动登录

**步骤**：
1. 清除小程序缓存（微信开发者工具 → 清缓存 → 全部清除）
2. 重新编译小程序
3. 观察控制台日志

**预期日志**：
```
Cshine 小程序启动
未登录
开始微信登录...
获取到 code: 0xxxxxxxxxxxx...
登录成功: { token: "...", user_id: "...", is_new_user: true }
```

**验证**：
- 控制台显示"登录成功"
- 本地存储中有 `token` 和 `userInfo`
- 后续 API 请求自动携带 Token

---

### 2. 测试完整授权登录

**步骤**：
1. 打开小程序
2. 切换到"我的"Tab
3. 点击"登录"按钮
4. 在弹窗中点击"允许"

**预期行为**：
- 显示 Loading："登录中..."
- 弹窗提示："用于完善用户资料"
- 登录成功后显示用户头像和昵称
- Toast 提示："欢迎使用 Cshine！"（新用户）或"登录成功"（老用户）

---

### 3. 测试退出登录

**步骤**：
1. 在"我的"页面点击"退出登录"
2. 确认弹窗

**预期行为**：
- 清除本地 Token 和用户信息
- 页面显示"未登录"状态
- 统计数据重置为 0

---

### 4. 测试 Token 失效

**模拟步骤**：
1. 手动清除本地 Token：`wx.removeStorageSync('token')`
2. 调用需要认证的 API（如创建闪记）

**预期行为**：
- 后端返回 401
- 自动清除本地数据
- 提示："登录已过期，请重新登录"

---

## 🔧 后端配置

### 微信小程序配置

在 `backend/config.py` 中配置：

```python
# 微信小程序配置
WECHAT_APPID = "your_appid"
WECHAT_SECRET = "your_appsecret"
```

获取方式：
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入"开发" → "开发管理" → "开发设置"
3. 复制 AppID 和 AppSecret

### JWT Token 配置

```python
# JWT 配置
JWT_SECRET_KEY = "your-secret-key-change-this-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 7 * 24 * 60  # 7 天
```

---

## 📱 前端配置

### API 地址配置

在 `utils/config.js` 中配置：

```javascript
// 开发环境（模拟器）
const API_BASE_URL = 'http://localhost:8000'

// 真机测试
const API_BASE_URL = 'http://192.168.x.x:8000'

// 生产环境
const API_BASE_URL = 'https://api.cshine.com'
```

---

## ⚠️ 注意事项

### 1. 微信登录限制

- `wx.login()` 的 code 有效期为 **5 分钟**
- code 只能使用 **一次**，使用后立即失效
- 每个用户每天最多调用 100 次

### 2. 用户信息授权

- `wx.getUserProfile()` 每次调用都需要用户授权
- 用户拒绝授权后，需要重新点击按钮才能再次弹窗
- 建议在用户首次登录时获取，后续使用本地缓存

### 3. Token 安全

- Token 存储在本地，有被窃取的风险
- 生产环境务必使用 HTTPS
- 设置合理的过期时间（建议 7 天）
- 敏感操作（如支付）需要二次验证

### 4. 生产环境部署

上线前必须配置：
1. ✅ 在微信公众平台配置服务器域名
2. ✅ 启用 HTTPS（微信小程序强制要求）
3. ✅ 修改 API_BASE_URL 为生产域名
4. ✅ 更换 JWT_SECRET_KEY

---

## 🐛 常见问题

### Q1: 登录按钮点击后无响应？

**可能原因**：
- 后端服务未启动
- API 地址配置错误
- 网络连接失败

**解决方法**：
1. 检查后端服务是否运行：`curl http://localhost:8000/health`
2. 检查 `utils/config.js` 的 API_BASE_URL
3. 查看控制台错误日志

---

### Q2: 提示"获取微信登录凭证失败"？

**可能原因**：
- 微信开发者工具未登录
- AppID 配置错误

**解决方法**：
1. 确保微信开发者工具已登录
2. 检查 `project.config.json` 的 appid
3. 重新编译小程序

---

### Q3: 后端返回 "Invalid WeChat code"？

**可能原因**：
- AppID 或 AppSecret 配置错误
- code 已过期或已使用
- 微信服务器异常

**解决方法**：
1. 检查 `backend/config.py` 的 WECHAT_APPID 和 WECHAT_SECRET
2. 确保 AppID 与小程序一致
3. 重新获取 code（重新登录）

---

### Q4: Token 总是失效？

**可能原因**：
- Token 过期时间太短
- 系统时间不同步
- JWT_SECRET_KEY 被修改

**解决方法**：
1. 增加 JWT_EXPIRE_MINUTES（如 7 天）
2. 检查服务器时间是否正确
3. 不要修改 JWT_SECRET_KEY（会导致所有 Token 失效）

---

## 📚 相关文件

### 前端
- `app.js` - 全局登录管理
- `pages/profile/profile.js` - 个人中心登录
- `utils/api.js` - 登录 API 封装
- `utils/request.js` - Token 自动携带
- `utils/config.js` - API 配置

### 后端
- `backend/app/api/auth.py` - 认证接口
- `backend/app/utils/wechat.py` - 微信登录
- `backend/app/utils/jwt.py` - JWT Token 生成
- `backend/app/dependencies.py` - 认证中间件
- `backend/config.py` - 配置文件

---

## 🔄 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.4.0 | 2025-11-08 | 完整实现前后端登录流程 |
| - | - | 添加自动静默登录 |
| - | - | 完善用户授权登录 |
| - | - | 优化 Token 管理和错误处理 |

---

**有问题？** 请查看 [后端文档](backend/README.md) 或提交 [Issue](https://github.com/cosmosva/Cshine/issues)

**Let Your Ideas Shine. ✨**

