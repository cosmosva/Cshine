# 🚀 线上后端登录功能更新指南

## 📋 更新内容

本次更新包含：
- ✅ 修复了 `/api/v1/auth/me` 接口的认证问题
- ✅ 完善了微信登录流程
- ✅ 优化了用户信息返回
- ✅ 环境配置自动检测（前端）

## ⚠️ 更新前检查

### 1. 确认生产环境配置

**SSH 到服务器后，检查 `.env` 配置：**

```bash
ssh cshine@your-server
cd ~/Cshine/backend
cat .env | grep -E "WECHAT_APPID|WECHAT_SECRET|OSS_BUCKET_NAME"
```

**必须确认：**
- `WECHAT_APPID=wx68cb1f3f6a2bcf17`
- `WECHAT_SECRET=73a2781f1c83d81f883f9957a02f8e01`
- `OSS_BUCKET_NAME=cshine-audio`（生产环境用生产bucket）

### 2. 备份数据库

```bash
cd ~/Cshine/backend
cp cshine.db cshine.db.backup.$(date +%Y%m%d_%H%M%S)
```

---

## 🚀 方案 A：使用自动部署脚本（推荐）

### 步骤 1：SSH 登录服务器

```bash
ssh cshine@your-server
# 或使用你配置的用户名和地址
```

### 步骤 2：运行更新脚本

```bash
cd ~/Cshine/backend
bash deploy/update.sh
```

**脚本会自动：**
1. ✅ 备份当前代码和配置
2. ✅ 拉取最新代码
3. ✅ 更新 Python 依赖
4. ✅ 运行数据库迁移（如有）
5. ✅ 重启服务
6. ✅ 健康检查

**预计耗时：** 2-3 分钟

---

## 🔧 方案 B：手动更新（如脚本失败）

### 步骤 1：SSH 登录

```bash
ssh cshine@your-server
```

### 步骤 2：进入项目目录

```bash
cd ~/Cshine
```

### 步骤 3：拉取最新代码

```bash
# 查看当前状态
git status

# 如果有未提交的更改，先暂存
git stash

# 拉取最新代码
git pull origin main

# 恢复暂存的更改（如有需要）
git stash pop
```

### 步骤 4：检查并更新配置

```bash
cd backend

# 检查 .env 文件
cat .env | grep WECHAT

# 如果微信配置缺失或错误，编辑 .env：
nano .env
```

**确保包含：**
```bash
WECHAT_APPID=wx68cb1f3f6a2bcf17
WECHAT_SECRET=73a2781f1c83d81f883f9957a02f8e01

# 生产环境使用生产 bucket
OSS_BUCKET_NAME=cshine-audio
```

### 步骤 5：激活虚拟环境并更新依赖

```bash
source venv/bin/activate

# 更新依赖（如果 requirements.txt 有变化）
pip install -r requirements.txt
```

### 步骤 6：重启服务

```bash
sudo systemctl restart cshine-api

# 等待几秒
sleep 3

# 检查服务状态
sudo systemctl status cshine-api
```

### 步骤 7：查看日志

```bash
# 实时查看系统日志
sudo journalctl -u cshine-api -f

# 或查看应用日志
tail -f ~/Cshine/backend/logs/cshine.log
```

---

## 🧪 更新后测试

### 1. 健康检查

```bash
curl http://127.0.0.1:8000/health
```

**期望返回：**
```json
{"status":"ok","version":"1.0.0"}
```

### 2. 测试登录接口

```bash
# 测试登录接口是否正常
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"code":"test123"}'
```

**期望返回：**
```json
{"detail":"微信登录失败：invalid code"}
```

这个错误是正常的（因为 code 不是真实的），说明接口工作正常。

### 3. 检查认证配置

```bash
cd ~/Cshine/backend
python -c "
from config import settings
print('=== 认证配置检查 ===')
print(f'AppID: {settings.WECHAT_APPID}')
print(f'Secret: {settings.WECHAT_SECRET[:10]}...')
print(f'OSS Bucket: {settings.OSS_BUCKET_NAME}')
"
```

### 4. 在小程序端测试

**使用体验版或正式版小程序：**
1. 清除缓存（开发者工具 → 清除缓存）
2. 重启小程序
3. 观察是否自动登录成功
4. 进入"我的"页面，查看是否显示用户信息

---

## 🔍 故障排查

### 问题 1：服务启动失败

**查看详细错误：**
```bash
sudo journalctl -u cshine-api -n 50 --no-pager
```

**常见原因：**
- ❌ 端口 8000 被占用
- ❌ 虚拟环境路径错误
- ❌ .env 配置缺失
- ❌ Python 依赖缺失

**解决方案：**
```bash
# 检查端口占用
sudo lsof -i :8000

# 检查 systemd 配置
sudo systemctl cat cshine-api

# 手动启动测试
cd ~/Cshine/backend
source venv/bin/activate
python main.py
```

---

### 问题 2：登录仍然失败

**检查微信配置：**
```bash
cd ~/Cshine/backend
python -c "
from config import settings
if not settings.WECHAT_APPID:
    print('❌ WECHAT_APPID 未配置')
elif not settings.WECHAT_SECRET:
    print('❌ WECHAT_SECRET 未配置')
else:
    print('✅ 微信配置正常')
    print(f'AppID: {settings.WECHAT_APPID}')
"
```

**如果配置缺失：**
```bash
# 编辑 .env
nano .env

# 添加这两行（使用你的实际值）
WECHAT_APPID=wx68cb1f3f6a2bcf17
WECHAT_SECRET=73a2781f1c83d81f883f9957a02f8e01

# 保存后重启服务
sudo systemctl restart cshine-api
```

---

### 问题 3：接口返回 401 Unauthorized

**可能原因：**
- Token 过期或无效
- `/me` 接口认证配置错误

**检查代码更新：**
```bash
cd ~/Cshine
git log --oneline -5 backend/app/api/auth.py
```

**应该能看到类似：**
```
fix: 修复 /me 接口的认证问题
```

**如果没有，重新拉取：**
```bash
git pull origin main
sudo systemctl restart cshine-api
```

---

### 问题 4：小程序报错"request:fail"

**可能原因：**
- 服务器未启动
- 域名配置问题
- HTTPS 证书问题

**检查服务器状态：**
```bash
curl https://cshine.xuyucloud.com/health
```

**检查 Nginx 配置：**
```bash
sudo nginx -t
sudo systemctl status nginx
```

---

## 📊 关键文件变化

### 本次更新涉及的文件

**后端：**
- `backend/app/api/auth.py` - 修复了 `/me` 接口
- `backend/config.py` - 添加了 OSS 环境配置说明

**前端：**
- `utils/config.js` - 添加了自动环境检测
- `pages/profile/profile.js` - 优化了登录流程
- `pages/profile/profile.wxml` - 改为"完善资料"

---

## ✅ 更新检查清单

**部署前：**
- [ ] 已备份生产数据库
- [ ] 确认 .env 配置正确
- [ ] 本地代码已提交到 main 分支

**部署中：**
- [ ] SSH 连接服务器成功
- [ ] 代码拉取成功
- [ ] 依赖更新完成
- [ ] 服务重启成功

**部署后：**
- [ ] 健康检查接口正常
- [ ] 登录接口响应正常
- [ ] 小程序能够成功登录
- [ ] 用户信息显示正常
- [ ] 数据上传功能正常

---

## 🎯 一键更新命令

**如果你想快速执行所有步骤：**

```bash
ssh cshine@your-server << 'EOF'
  echo "🚀 开始更新 Cshine 后端..."
  
  # 进入目录
  cd ~/Cshine
  
  # 备份数据库
  cp backend/cshine.db backend/cshine.db.backup.$(date +%Y%m%d_%H%M%S)
  
  # 拉取代码
  git pull origin main
  
  # 进入后端目录
  cd backend
  
  # 激活虚拟环境
  source venv/bin/activate
  
  # 更新依赖（如果需要）
  pip install -r requirements.txt --quiet
  
  # 重启服务
  sudo systemctl restart cshine-api
  
  # 等待启动
  sleep 3
  
  # 检查状态
  if systemctl is-active --quiet cshine-api; then
    echo "✅ 服务启动成功"
    curl -s http://127.0.0.1:8000/health
  else
    echo "❌ 服务启动失败"
    sudo journalctl -u cshine-api -n 20 --no-pager
  fi
  
  echo ""
  echo "🎉 更新完成！"
EOF
```

---

## 📞 需要帮助？

如果更新过程中遇到问题：

1. **查看完整错误日志：**
   ```bash
   sudo journalctl -u cshine-api -n 100 --no-pager
   ```

2. **查看应用日志：**
   ```bash
   tail -n 100 ~/Cshine/backend/logs/cshine.log
   ```

3. **回滚到上一版本：**
   ```bash
   cd ~/Cshine/backend
   bash deploy/rollback.sh
   ```

4. **联系我：** 提供错误信息，我会帮你解决！

---

## 🎉 更新成功后

**验证登录功能：**
1. 使用正式版小程序
2. 清除缓存
3. 重启小程序
4. 应该自动静默登录
5. 进入"我的"页面
6. 显示"Cshine用户"（未完善资料）或真实头像昵称（已完善）

**一切正常！** 🚀

