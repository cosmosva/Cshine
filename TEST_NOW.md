# 🚀 实时测试指南

> 后端服务已启动！现在开始测试

## ✅ 服务状态

```
✅ 后端服务：运行中 (PID: 14373)
✅ 端口：8000
✅ 健康检查：通过
✅ 数据库：已连接
✅ OSS 存储：已连接
✅ 微信配置：已加载
```

---

## 📱 第 1 步：打开微信开发者工具

如果还没打开，请打开微信开发者工具并导入项目：
```
项目路径：/Users/cosmos_pro/Documents/文稿 - cosmos/CODE/CP/Cshine
```

---

## 🧹 第 2 步：清除缓存（重要！）

在微信开发者工具中：

1. 点击菜单栏：**工具**
2. 选择：**清除缓存**
3. 点击：**全部清除**
4. 确认清除

⚠️ **为什么要清除缓存？**
- 清除旧的 Token 和登录状态
- 确保测试从头开始
- 验证自动登录流程

---

## 🔄 第 3 步：重新编译

点击开发者工具右上角的 **"编译"** 按钮

---

## 👀 第 4 步：观察控制台日志

**在开发者工具的 Console 面板观察：**

### ✅ 预期日志序列：

```javascript
// 1. 应用启动
"Cshine 小程序启动"

// 2. 检查登录状态
"未登录"

// 3. 开始自动登录
"开始微信登录..."

// 4. 获取登录凭证
"获取到 code: 071xxxxx..."

// 5. 调用后端 API
"[API] POST /api/v1/auth/login"

// 6. 登录成功 🎉
"后端登录成功: { 
  token: 'eyJhbGc...',
  user_id: 'xxx-xxx-xxx',
  is_new_user: true 
}"

// 7. 加载首页
"首页加载"
```

---

## ✅ 第 5 步：验证登录状态

### 方法 1：在控制台验证

在 Console 中执行以下命令：

```javascript
// 检查 Token
wx.getStorageSync('token')
// 应返回：长字符串，如 "eyJhbGciOiJIUzI1NiIsInR..."

// 检查用户信息
wx.getStorageSync('userInfo')
// 应返回：{ id: "...", nickname: "Cshine用户", ... }

// 检查全局状态
getApp().globalData.token
// 应返回：Token 字符串
```

### 方法 2：在页面上验证

**首页应该显示：**
- ✅ "Let Your Ideas Shine" 品牌区域
- ✅ "今天已记录 0 条灵感"
- ✅ 录音按钮（蓝色渐变圆形）
- ✅ "最近记录" 筛选器
- ✅ 空状态提示（如果还没有数据）

**我的页面应该显示：**
- ✅ 默认头像
- ✅ 昵称："Cshine用户"（静默登录的默认昵称）
- ✅ 统计数据卡片
- ✅ 功能菜单

---

## 🎙️ 第 6 步：测试录音功能

### 录音测试步骤：

1. **回到首页**
2. **长按中央录音按钮**
3. **对着麦克风说话 5-10 秒**
   - 例如："这是一条测试语音，测试登录功能是否正常"
4. **松开手指**

### ✅ 预期行为：

```
🎤 录音中
  ↓
📤 上传音频
  ↓
⏳ "AI 正在处理..."
  ↓
✅ 显示转写结果
  ↓
🎉 "AI 分析完成！"
```

### 观察 Network 请求：

在开发者工具的 **Network** 面板查看：

```
POST /api/v1/upload/audio
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR...
Status: 200 OK

POST /api/v1/flash/create
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR...
Status: 200 OK
```

⚠️ **关键验证点**：
- Authorization header 应该自动添加
- Token 格式正确（Bearer + 空格 + Token）
- 返回状态是 200

---

## 🎉 第 7 步：确认测试成功

如果以上步骤都正常，说明登录功能测试通过！

### 测试成功标志：

- [x] ✅ 小程序启动时自动登录
- [x] ✅ 控制台显示完整登录流程
- [x] ✅ Token 正确保存到本地存储
- [x] ✅ 全局状态正确更新
- [x] ✅ 首页数据正常显示
- [x] ✅ 录音功能正常工作
- [x] ✅ API 请求自动携带 Token
- [x] ✅ 后端正确验证 Token

---

## 🔍 故障排查

### 问题 1：没有看到登录日志

**可能原因**：
- Console 面板没有选中
- 日志被过滤了

**解决方法**：
1. 确保在 Console 面板
2. 清空日志后重新编译
3. 检查日志级别设置

---

### 问题 2：提示 "Invalid WeChat code"

**检查后端日志**：
```bash
cd /Users/cosmos_pro/Documents/文稿\ -\ cosmos/CODE/CP/Cshine/backend
tail -50 server.log | grep -i error
```

**可能原因**：
- code 已过期（重新编译小程序）
- 网络问题（微信服务器无响应）
- AppID/Secret 配置错误（已排除，我们刚配置的）

**解决方法**：
```bash
# 1. 验证配置
cd backend
cat .env | grep WECHAT

# 2. 重启后端（刷新配置）
kill $(cat server.pid)
source venv/bin/activate
python main.py &
```

---

### 问题 3：Token 没有保存

**检查**：
```javascript
// 1. 查看 API 响应
// 在 Network 面板查看 /api/v1/auth/login 的响应

// 2. 查看存储操作
// 在 app.js doLogin() 中是否执行了 wx.setStorageSync
```

**解决方法**：
- 检查 `app.js` 的 doLogin() 方法
- 确保 Token 保存逻辑正确

---

### 问题 4：录音上传失败

**检查 OSS 配置**：
```bash
cd backend
cat .env | grep OSS
```

**查看后端日志**：
```bash
tail -50 server.log | grep -i oss
```

**可能原因**：
- OSS 配置错误
- 权限不足
- 网络问题

---

## 📊 后端实时日志

查看后端实时日志：

```bash
cd /Users/cosmos_pro/Documents/文稿\ -\ cosmos/CODE/CP/Cshine/backend
tail -f server.log
```

**重要日志关键词**：
- `Login error` - 登录失败
- `Invalid WeChat code` - 微信验证失败
- `Token` - Token 相关
- `OSS` - 文件上传
- `ERROR` - 错误信息

---

## 🎯 下一步测试

### 基础测试通过后，可以测试：

1. **手动授权登录**
   - 切换到"我的"Tab
   - 点击"登录"按钮
   - 授权获取昵称和头像

2. **退出登录**
   - 点击"退出登录"
   - 确认清除数据
   - 重新登录

3. **Token 失效测试**
   - 手动清除 Token
   - 触发 API 调用
   - 验证自动重新登录

4. **会议纪要功能**
   - 切换到"知识库"Tab
   - 上传音频文件
   - 测试 AI 处理

---

## 📝 测试记录

**测试时间**：2025-11-09 01:38

**测试环境**：
- 后端：✅ 运行中
- 前端：⏳ 待测试
- 数据库：✅ 已连接
- OSS：✅ 已连接

**测试结果**：
- [ ] 自动登录
- [ ] Token 保存
- [ ] 首页加载
- [ ] 录音功能
- [ ] API 调用

---

## 🛑 停止后端服务

测试完成后，可以停止后端服务：

```bash
cd /Users/cosmos_pro/Documents/文稿\ -\ cosmos/CODE/CP/Cshine/backend
kill $(cat server.pid)
echo "✅ 服务已停止"
```

---

## 📚 相关命令

```bash
# 查看服务状态
curl http://localhost:8000/health

# 查看实时日志
tail -f backend/server.log

# 重启服务
cd backend
kill $(cat server.pid)
python main.py &

# 查看端口占用
lsof -i:8000

# 查看数据库
sqlite3 backend/cshine.db "SELECT * FROM users;"
```

---

**现在开始测试吧！** 🚀

有任何问题随时告诉我，我会实时帮你解决！

