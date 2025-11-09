# Cshine 登录功能文档

> 最后更新：2025-11-09  
> 版本：v0.4.2

## 📋 概述

Cshine 使用微信小程序登录系统，支持两种登录方式：
1. **自动静默登录**：小程序启动时自动登录（不需要用户授权）
2. **完善资料**：用户在个人中心主动授权（获取昵称和头像）

---

## 🔐 登录流程

### 1. 自动静默登录

**触发时机**：小程序启动时自动执行

**流程**：
```
小程序启动 (app.js onLaunch)
    ↓
检查本地 Token
    ↓
Token 不存在？
    ↓ 是
调用 wx.login() 获取 code
    ↓
调用后端 API /api/v1/auth/login
    ↓
保存 Token 和 user_id
    ↓
登录完成（用户无感知）
```

**优点**：用户无感知，快速启动

---

### 2. 完善资料（获取头像昵称）

**触发时机**：用户在"我的"页面点击"完善资料"按钮

**流程**：
```
用户点击"完善资料"
    ↓
调用 wx.getUserProfile()（必须在点击事件中同步调用）
    ↓
用户授权成功
    ↓
调用 wx.login() 获取 code
    ↓
调用后端 API /api/v1/auth/login（带用户信息）
    ↓
保存 Token、user_id、nickname、avatar
    ↓
更新页面显示
```

**注意**：`wx.getUserProfile()` 必须在用户点击事件的同步上下文中调用

---

## 🔑 Token 管理

### 存储位置

| Key | 说明 | 示例 |
|-----|------|------|
| `token` | JWT Token | `eyJhbGciOiJIUzI1...` |
| `userInfo` | 用户信息 | `{ id, nickname, avatar }` |

### 自动携带

所有 API 请求自动在 Header 中携带 Token：
```javascript
Authorization: Bearer ${token}
```

### Token 失效处理

当后端返回 `401 Unauthorized` 时：
1. 自动清除本地 Token
2. 提示："登录已过期，请重新登录"
3. 重新打开小程序触发自动登录

---

## 🌍 环境配置

### 自动环境检测

系统自动根据运行环境选择 API 地址：

| 运行场景 | 环境 | API 地址 |
|---------|------|----------|
| 微信开发者工具 | development | `http://192.168.80.50:8000` |
| 开发版/预览 | development | `http://192.168.80.50:8000` |
| 体验版 | production | `https://cshine.xuyucloud.com` |
| 正式版 | production | `https://cshine.xuyucloud.com` |

**配置位置**：`utils/config.js`

---

## 🧪 测试指南

### 测试前准备

1. **配置微信 AppID 和 Secret**
   ```bash
   cd backend
   cp .env.example .env
   # 编辑 .env，填入 WECHAT_APPID 和 WECHAT_SECRET
   ```

2. **启动后端服务**
   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

3. **验证服务**
   ```bash
   curl http://localhost:8000/health
   # 应返回: {"status":"healthy"}
   ```

### 测试场景

#### 场景 1：自动静默登录

**步骤**：
1. 清除小程序缓存
2. 重新编译小程序
3. 观察控制台日志

**预期日志**：
```
Cshine 小程序启动
未登录
开始微信登录...
获取到 code: 071xxxxx...
登录成功: { token: "...", user_id: "...", is_new_user: true }
```

#### 场景 2：完善资料

**步骤**：
1. 进入"我的"页面
2. 点击"完善资料"按钮
3. 允许授权

**预期结果**：
- 显示用户头像和昵称
- 提示"资料已完善"

#### 场景 3：Token 失效

**模拟**：
1. 手动清除 Token：`wx.removeStorageSync('token')`
2. 调用需要认证的 API

**预期**：
- 后端返回 401
- 自动清除本地数据
- 提示重新登录

---

## 🔧 配置说明

### 后端配置

**文件**：`backend/.env`

```bash
WECHAT_APPID=wx68cb1f3f6a2bcf17
WECHAT_SECRET=your_secret
SECRET_KEY=your-jwt-secret-key
```

### 前端配置

**文件**：`utils/config.js`

自动检测环境，无需手动配置。

---

## ⚠️ 注意事项

1. **微信登录限制**
   - `wx.login()` 的 code 有效期 5 分钟
   - code 只能使用一次
   - 每天最多调用 100 次

2. **用户信息授权**
   - `wx.getUserProfile()` 必须在点击事件中同步调用
   - 每次调用都需要用户授权
   - 用户拒绝后需重新点击

3. **Token 安全**
   - 生产环境必须使用 HTTPS
   - 设置合理的过期时间（默认 7 天）
   - 不要泄露 JWT_SECRET_KEY

---

## 🐛 常见问题

### Q1: 登录按钮点击后无响应？

**检查**：
- 后端服务是否运行
- API 地址配置是否正确
- 查看控制台错误日志

### Q2: 提示"获取微信登录凭证失败"？

**检查**：
- 微信开发者工具是否已登录
- `project.config.json` 的 appid 是否正确

### Q3: 后端返回 "Invalid WeChat code"？

**检查**：
- AppID 或 AppSecret 配置是否正确
- code 是否已过期或已使用

### Q4: getUserProfile 报错？

**错误**：`getUserProfile:fail can only be invoked by user TAP gesture`

**解决**：确保 `wx.getUserProfile()` 在点击事件的同步上下文中调用

---

## 📚 相关文件

**前端**：
- `app.js` - 全局登录管理
- `pages/profile/profile.js` - 个人中心登录
- `utils/api.js` - 登录 API 封装
- `utils/request.js` - Token 自动携带
- `utils/config.js` - 环境配置

**后端**：
- `backend/app/api/auth.py` - 认证接口
- `backend/app/utils/wechat.py` - 微信登录
- `backend/app/utils/jwt.py` - JWT Token
- `backend/config.py` - 配置文件

---

**Let Your Ideas Shine. ✨**

