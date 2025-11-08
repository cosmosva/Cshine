# 登录功能测试指南

> v0.4.0 登录功能完整测试步骤

## 📋 测试前准备

### 1. 配置微信 AppID 和 Secret

**必须完成！** 否则无法测试登录功能。

```bash
# 1. 创建 .env 文件
cd backend
cp .env.example .env

# 2. 编辑 .env，填入你的 AppID 和 Secret
# 获取方式见：WECHAT_CONFIG_GUIDE.md
```

### 2. 启动后端服务

```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
python main.py             # 启动服务
```

**验证服务启动成功：**
- 浏览器访问：http://localhost:8000/health
- 应返回：`{"status": "healthy"}`

### 3. 配置小程序 API 地址

编辑 `utils/config.js`：

```javascript
// 模拟器测试
const API_BASE_URL = 'http://localhost:8000'

// 真机测试
// const API_BASE_URL = 'http://192.168.x.x:8000'
```

---

## 🧪 测试场景

### 场景 1：自动静默登录（推荐先测这个）

**目的**：验证小程序启动时自动登录

**步骤**：

1. **清除所有数据**
```
微信开发者工具 → 工具 → 清除缓存 → 全部清除
```

2. **重新编译小程序**
```
点击"编译"按钮
```

3. **观察控制台日志**

**预期日志**：
```
Cshine 小程序启动
未登录
开始微信登录...
获取到 code: 071xxxxx...
[API] POST /api/v1/auth/login
登录成功: { token: "eyJhbG...", user_id: "xxx", is_new_user: true }
首页加载
```

4. **检查本地存储**

在控制台执行：
```javascript
wx.getStorageSync('token')
wx.getStorageSync('userInfo')
```

**预期结果**：
- token: `"eyJhbGciOiJIUzI1NiIsInR5cCI6Ik..."`
- userInfo: `{ id: "xxx", nickname: "Cshine用户", ... }`

5. **验证首页数据加载**

**预期行为**：
- 首页正常显示"欢迎区域"
- 可以看到"今天已记录 0 条灵感"
- 可以点击录音按钮

---

### 场景 2：完整授权登录（获取昵称头像）

**目的**：验证用户主动授权登录

**步骤**：

1. **切换到"我的"Tab**

2. **如果已登录，先退出**
- 点击"退出登录"
- 确认弹窗

3. **点击"登录"按钮**

**预期行为**：
- 显示 Loading："登录中..."
- 弹出微信授权窗口："用于完善用户资料"

4. **点击"允许"授权**

**预期行为**：
- 显示用户头像和昵称
- Toast 提示："欢迎使用 Cshine！"（新用户）或"登录成功"（老用户）
- 显示统计数据

5. **观察控制台日志**

**预期日志**：
```
微信登录 code: 071xxxxx...
用户信息: { nickName: "xxx", avatarUrl: "https://..." }
后端登录成功: { token: "...", user_id: "...", is_new_user: false }
```

6. **验证数据持久化**

刷新小程序（重新编译），应该：
- 自动登录成功
- 显示用户昵称和头像
- 无需重新授权

---

### 场景 3：Token 自动携带测试

**目的**：验证 API 请求自动携带 Token

**步骤**：

1. **确保已登录**（完成场景1或2）

2. **录制一条闪记**
- 进入首页
- 长按录音按钮
- 说话10秒
- 松开

3. **观察网络请求**

在开发者工具"Network"面板查看：

**预期请求头**：
```
POST /api/v1/upload/audio
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...
```

4. **验证API成功调用**

**预期响应**：
```json
{
  "code": 200,
  "data": {
    "flash_id": "xxx",
    "audio_url": "https://..."
  }
}
```

---

### 场景 4：Token 失效处理

**目的**：验证 Token 过期后的处理

**模拟步骤**：

1. **手动清除 Token**

在控制台执行：
```javascript
wx.removeStorageSync('token')
```

2. **尝试调用需要登录的接口**

例如：下拉刷新首页列表

3. **观察行为**

**预期行为**：
- 后端返回 401 错误
- 自动清除本地数据
- Toast 提示："登录已过期，请重新登录"
- 自动重新登录（静默）

4. **验证自动恢复**

**预期行为**：
- 小程序自动调用 `app.ensureLogin()`
- 重新获取 Token
- 数据正常加载

---

### 场景 5：网络异常处理

**目的**：验证网络错误时的处理

**步骤**：

1. **停止后端服务**
```bash
# 在后端终端按 Ctrl+C
```

2. **清除缓存并重新编译**

3. **观察行为**

**预期行为**：
- Toast 提示："网络连接失败，请检查网络"
- 不会无限循环请求
- 页面不会卡死

4. **重启后端服务**

**预期行为**：
- 下次操作时自动恢复
- 成功调用 API

---

### 场景 6：页面登录保护测试

**目的**：验证所有页面都有登录检查

**步骤**：

1. **确保未登录状态**
```javascript
wx.clearStorage()  // 清除所有数据
```

2. **尝试访问各个页面**

测试页面列表：
- 首页（Tab）
- 会议列表（Tab）
- 详情页（需要从首页跳转）
- 编辑页（需要从详情页跳转）
- 会议上传页
- 会议详情页

**预期行为**：
- 首页和会议列表：自动静默登录
- 详情页和编辑页：Toast "请先登录" → 跳转到个人中心
- 所有需要登录的 API 都返回 401（如果Token无效）

---

## ✅ 测试检查清单

### 基础功能

- [ ] ⬜ 小程序启动时自动登录
- [ ] ⬜ 登录成功后保存 Token
- [ ] ⬜ Token 自动携带到所有 API 请求
- [ ] ⬜ 401 错误自动清除 Token
- [ ] ⬜ 个人中心点击登录可以授权
- [ ] ⬜ 退出登录清除所有数据

### 页面保护

- [ ] ⬜ 首页有登录检查
- [ ] ⬜ 会议列表有登录检查  
- [ ] ⬜ 详情页有登录检查
- [ ] ⬜ 编辑页有登录检查
- [ ] ⬜ 会议上传页有登录检查
- [ ] ⬜ 会议详情页有登录检查

### 后端接口

- [ ] ⬜ `/api/v1/auth/login` 可以无需 Token 调用
- [ ] ⬜ `/api/v1/auth/me` 需要 Token
- [ ] ⬜ `/api/v1/flash/*` 所有接口需要 Token
- [ ] ⬜ `/api/v1/meeting/*` 所有接口需要 Token
- [ ] ⬜ `/api/v1/upload/audio` 需要 Token

### 异常处理

- [ ] ⬜ 网络异常有友好提示
- [ ] ⬜ Token 失效自动重新登录
- [ ] ⬜ 授权拒绝有提示
- [ ] ⬜ 后端服务停止不会卡死

---

## 🐛 常见问题排查

### Q1: 提示"Invalid WeChat code"

**检查项**：
1. ✅ `backend/.env` 中的 `WECHAT_APPID` 和 `WECHAT_SECRET` 是否正确
2. ✅ AppID 是否与小程序一致（`project.config.json` 中的 appid）
3. ✅ code 是否已过期（重新编译小程序）

**解决方法**：
```bash
# 1. 检查配置
cat backend/.env | grep WECHAT

# 2. 查看后端日志
tail -f backend/logs/cshine.log

# 3. 重新编译小程序
```

---

### Q2: Token 无法携带到请求

**检查项**：
1. ✅ Token 是否正确保存：`wx.getStorageSync('token')`
2. ✅ `request.js` 是否正确添加 Authorization 头
3. ✅ API 请求是否设置了 `needAuth: true`（默认）

**调试方法**：
```javascript
// 在 request.js 的 request 函数中添加日志
console.log('Token:', token)
console.log('Request Header:', requestHeader)
```

---

### Q3: 登录成功但数据加载失败

**检查项**：
1. ✅ 后端接口是否正确使用 `get_current_user` 依赖
2. ✅ JWT Token 是否正确解析
3. ✅ 数据库中是否有用户数据

**调试方法**：
```bash
# 查看后端日志
tail -f backend/logs/cshine.log

# 检查数据库
sqlite3 backend/cshine.db "SELECT * FROM users;"
```

---

### Q4: 页面白屏或卡死

**检查项**：
1. ✅ 后端服务是否正常运行
2. ✅ 网络请求是否超时
3. ✅ 是否有未捕获的异常

**解决方法**：
```javascript
// 在页面 onLoad 中添加 try-catch
async onLoad() {
  try {
    await app.ensureLogin()
    // ... 其他代码
  } catch (error) {
    console.error('页面加载失败:', error)
    showError('页面加载失败')
  }
}
```

---

## 📊 测试报告模板

完成测试后，请填写以下报告：

```
测试时间：2025-11-XX
测试环境：微信开发者工具 / 真机 (iOS/Android)
测试版本：v0.4.0

✅ 通过的测试（x/14）
- 自动登录
- 手动授权登录
- ...

❌ 失败的测试
- XXX功能：错误描述

⚠️ 发现的问题
1. 问题描述
2. 复现步骤
3. 预期行为 vs 实际行为
```

---

## 🚀 测试通过后

恭喜！登录功能测试通过。

### 下一步：

1. **提交代码**
```bash
git add .
git commit -m "test: 登录功能测试通过"
```

2. **真机测试**
- 修改 API_BASE_URL 为真实服务器 IP
- 在真机上完整测试一遍

3. **开始开发新功能**
- 搜索功能
- 文件夹管理
- 分享功能

---

**测试遇到问题？** 查看 [LOGIN_GUIDE.md](LOGIN_GUIDE.md) 或 [TROUBLESHOOTING.md](backend/TROUBLESHOOTING.md)

