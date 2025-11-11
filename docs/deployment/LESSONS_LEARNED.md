# 线上部署经验教训

> **重要**：这是从实际部署中总结的经验教训，每次部署前必读！

## 📋 目录

- [部署前检查清单](#部署前检查清单)
- [常见问题及解决方案](#常见问题及解决方案)
- [关键配置检查](#关键配置检查)
- [调试技巧](#调试技巧)
- [回滚策略](#回滚策略)

---

## 🎯 部署前检查清单

### 1. 代码推送检查

- [ ] **本地提交已推送到远程仓库**
  - ❌ 常见错误：只 `git commit` 没有 `git push`
  - ✅ 正确做法：`git commit` + `git push origin main`
  - 💡 验证：在 GitHub 上确认最新提交

### 2. 环境配置检查

- [ ] **服务器环境变量正确**
  - Python 版本：`python3.11`（不是 `python`）
  - 虚拟环境路径：`/home/cshine/Cshine/venv`（项目根目录）
  - 数据库配置：使用 `DATABASE_URL` 而不是独立字段

- [ ] **小程序配置正确**
  - 生产环境必须使用 HTTPS 域名
  - ❌ 错误：`http://8.134.254.88:8000`
  - ✅ 正确：`https://cshine.xuyucloud.com`

### 3. 数据库迁移检查

- [ ] **迁移脚本适配服务器环境**
  - 使用 `DATABASE_URL` 解析连接信息
  - 初始化 `conn = None` 和 `cursor = None`
  - 使用 `python3.11` 执行迁移脚本

### 4. 服务重启检查

- [ ] **完整的重启流程**
  1. 拉取最新代码：`git pull origin main`
  2. 执行数据库迁移（如果有）
  3. 重启服务：`sudo systemctl restart cshine-api`
  4. 验证服务状态：`sudo systemctl status cshine-api`
  5. 健康检查：`curl http://localhost:8000/health`

---

## 🐛 常见问题及解决方案

### 问题 1：503 错误 - 服务未响应

**症状**：
- 小程序报 503 错误
- `curl http://localhost:8000/health` 无响应

**可能原因**：
1. 服务未启动
2. 服务启动失败
3. 代码未更新

**解决步骤**：
```bash
# 1. 检查服务状态
sudo systemctl status cshine-api

# 2. 查看服务日志
sudo journalctl -u cshine-api -n 50

# 3. 如果服务未运行，重启
sudo systemctl restart cshine-api

# 4. 验证健康检查
curl http://localhost:8000/health
curl https://cshine.xuyucloud.com/health
```

### 问题 2：数据库迁移失败 - `DB_HOST` 不存在

**症状**：
```
AttributeError: 'Settings' object has no attribute 'DB_HOST'
```

**原因**：
- 服务器配置使用 `DATABASE_URL` 连接字符串
- 迁移脚本尝试访问不存在的 `settings.DB_HOST`

**解决方案**：
```python
# ❌ 错误写法
conn = psycopg2.connect(
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD
)

# ✅ 正确写法
from urllib.parse import urlparse

db_url = urlparse(settings.DATABASE_URL)
conn = psycopg2.connect(
    host=db_url.hostname,
    port=db_url.port or 5432,
    database=db_url.path.lstrip('/'),
    user=db_url.username,
    password=db_url.password
)
```

### 问题 3：虚拟环境路径错误

**症状**：
```
-bash: venv/bin/activate: No such file or directory
```

**原因**：
- 虚拟环境在项目根目录 `/home/cshine/Cshine/venv`
- 脚本在 `backend` 目录下尝试激活 `venv/bin/activate`

**解决方案**：
```bash
# ❌ 错误（在 backend 目录下）
source venv/bin/activate

# ✅ 正确（切换到项目根目录）
cd ~/Cshine
source venv/bin/activate
cd backend
```

### 问题 4：Python 命令错误

**症状**：
```
python: command not found
```

**原因**：
- 服务器上 Python 3.11 的命令是 `python3.11`
- 不是 `python` 或 `python3`

**解决方案**：
```bash
# ❌ 错误
python migrations/xxx.py

# ✅ 正确
python3.11 migrations/xxx.py
```

### 问题 5：小程序 503 但服务器正常

**症状**：
- `curl http://localhost:8000/health` 返回正常
- `curl https://cshine.xuyucloud.com/health` 返回正常
- 小程序体验版报 503 错误

**原因**：
- 小程序配置使用了 HTTP 或 IP 地址
- 微信小程序要求使用 HTTPS 域名

**解决方案**：
```javascript
// ❌ 错误配置
const API_CONFIG = {
  production: 'http://8.134.254.88:8000'  // HTTP + IP
}

// ✅ 正确配置
const API_CONFIG = {
  production: 'https://cshine.xuyucloud.com'  // HTTPS + 域名
}
```

### 问题 6：代码更新但服务未生效

**症状**：
- 服务器代码已更新（`git log` 显示最新提交）
- 服务状态显示 `active (running)`
- 但功能仍然是旧的

**原因**：
- 代码更新后未重启服务
- 旧的 Python 进程仍在运行

**解决方案**：
```bash
# 必须重启服务让新代码生效
sudo systemctl restart cshine-api

# 验证进程启动时间
ps aux | grep uvicorn
sudo systemctl status cshine-api  # 查看 Active 时间
```

---

## 🔑 关键配置检查

### 服务器端配置

#### 1. Systemd 服务配置
```ini
# /etc/systemd/system/cshine-api.service
[Service]
WorkingDirectory=/home/cshine/Cshine/backend  # 工作目录
ExecStart=/usr/bin/python3.11 -m uvicorn ...  # 使用 python3.11
```

#### 2. Nginx 配置
```nginx
# /etc/nginx/sites-available/cshine
server {
    server_name cshine.xuyucloud.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;  # 反向代理到后端
        # ... 其他配置
    }
    
    listen 443 ssl;  # HTTPS
    ssl_certificate /etc/letsencrypt/live/cshine.xuyucloud.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cshine.xuyucloud.com/privkey.pem;
}
```

#### 3. 数据库配置
```python
# backend/config.py
class Settings(BaseSettings):
    DATABASE_URL: str = Field(
        default="sqlite:///./cshine.db",
        description="数据库连接字符串"
    )
    # 注意：不是 DB_HOST, DB_PORT 等独立字段
```

### 小程序端配置

#### 1. API 地址配置
```javascript
// utils/config.js
const API_CONFIG = {
  development: 'http://localhost:8000',           // 开发环境
  production: 'https://cshine.xuyucloud.com'      // 生产环境（必须 HTTPS）
}
```

#### 2. 环境检测
```javascript
function getEnvironment() {
  const accountInfo = wx.getAccountInfoSync()
  const envVersion = accountInfo.miniProgram.envVersion
  
  // 'release'  - 正式版 → production
  // 'trial'    - 体验版 → production
  // 'develop'  - 开发版 → development
  // undefined  - 开发工具 → development
  
  if (envVersion === 'release' || envVersion === 'trial') {
    return 'production'
  } else {
    return 'development'
  }
}
```

---

## 🔍 调试技巧

### 1. 快速验证服务状态

```bash
# 一键验证脚本
echo "=== 服务状态 ==="
sudo systemctl status cshine-api | head -5

echo -e "\n=== 本地健康检查 ==="
curl http://localhost:8000/health

echo -e "\n=== 外网健康检查 ==="
curl https://cshine.xuyucloud.com/health

echo -e "\n=== 端口监听 ==="
sudo netstat -tlnp | grep 8000

echo -e "\n=== 进程信息 ==="
ps aux | grep uvicorn | grep -v grep
```

### 2. 查看实时日志

```bash
# Systemd 日志（推荐）
sudo journalctl -u cshine-api -f

# 应用日志
tail -f /home/cshine/Cshine/backend/logs/uvicorn.log
tail -f /home/cshine/Cshine/backend/logs/uvicorn.error.log

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. 验证数据库迁移

```bash
# PostgreSQL
sudo -u postgres psql cshine_db -c "
  SELECT table_name 
  FROM information_schema.tables 
  WHERE table_schema = 'public' 
  ORDER BY table_name;
"

# 检查特定表是否存在
sudo -u postgres psql cshine_db -c "
  SELECT COUNT(*) 
  FROM information_schema.tables 
  WHERE table_name IN ('contacts', 'meeting_speakers');
"
```

### 4. 测试 Nginx 反向代理

```bash
# 测试后端直连
curl -v http://127.0.0.1:8000/health

# 测试 Nginx 代理（HTTP）
curl -v http://localhost/health

# 测试 Nginx 代理（HTTPS）
curl -v https://cshine.xuyucloud.com/health

# 从外网测试（在本地执行）
curl -v https://cshine.xuyucloud.com/health
```

---

## 🔄 回滚策略

### 快速回滚步骤

```bash
# 1. 切换到上一个稳定版本
cd /home/cshine/Cshine
git log --oneline -10  # 查看最近提交
git reset --hard <稳定版本的commit-hash>

# 2. 重启服务
sudo systemctl restart cshine-api

# 3. 验证
curl http://localhost:8000/health
```

### 数据库回滚

```bash
# 1. 查看备份
ls -lh /home/cshine/Cshine/backend/backup_*.sql

# 2. 恢复备份
sudo -u postgres psql cshine_db < backup_before_vX.X.X_YYYYMMDD_HHMMSS.sql

# 3. 重启服务
sudo systemctl restart cshine-api
```

---

## 📚 标准部署流程（完整版）

### 阶段 1：本地准备

```bash
# 1. 确保所有改动已提交
git status
git add -A
git commit -m "feat: xxx"

# 2. 推送到远程仓库（关键！）
git push origin main

# 3. 验证推送成功
# 在 GitHub 上确认最新提交
```

### 阶段 2：服务器更新

```bash
# 1. SSH 登录服务器
ssh cshine@8.134.254.88

# 2. 进入项目目录
cd /home/cshine/Cshine

# 3. 停止服务
sudo systemctl stop cshine-api

# 4. 备份数据库（如果有数据库变更）
cd backend
sudo -u postgres pg_dump cshine_db > backup_$(date +%Y%m%d_%H%M%S).sql
cd ..

# 5. 拉取最新代码
git fetch origin
git pull origin main

# 6. 查看更新内容
git log --oneline -5

# 7. 执行数据库迁移（如果有）
cd backend
python3.11 migrations/xxx.py
cd ..

# 8. 重启服务
sudo systemctl restart cshine-api

# 9. 验证服务状态
sudo systemctl status cshine-api
curl http://localhost:8000/health
curl https://cshine.xuyucloud.com/health
```

### 阶段 3：小程序更新

```bash
# 1. 确保小程序配置正确
# utils/config.js 中 production 必须是 https://cshine.xuyucloud.com

# 2. 在微信开发者工具中上传
# - 版本号：v0.5.x
# - 更新说明：简要描述更新内容

# 3. 在小程序后台设置为体验版

# 4. 测试体验版功能
```

---

## ⚠️ 关键注意事项

### 1. 永远不要忘记 `git push`

- ❌ 只 `git commit` 不 `git push`
- ✅ `git commit` + `git push origin main`
- 💡 养成习惯：提交后立即推送

### 2. 服务器环境与本地不同

| 配置项 | 本地开发 | 服务器生产 |
|--------|---------|-----------|
| Python 命令 | `python` | `python3.11` |
| 虚拟环境 | `backend/venv` | `/home/cshine/Cshine/venv` |
| 数据库配置 | 独立字段 | `DATABASE_URL` |
| API 地址 | `localhost:8000` | `https://cshine.xuyucloud.com` |

### 3. 小程序必须使用 HTTPS

- ❌ `http://8.134.254.88:8000`
- ❌ `http://cshine.xuyucloud.com`
- ✅ `https://cshine.xuyucloud.com`

### 4. 代码更新后必须重启服务

- 拉取代码 ≠ 服务更新
- 必须执行 `sudo systemctl restart cshine-api`

### 5. 数据库迁移必须在重启前执行

```bash
# ✅ 正确顺序
git pull
python3.11 migrations/xxx.py  # 先迁移
sudo systemctl restart cshine-api  # 后重启

# ❌ 错误顺序
git pull
sudo systemctl restart cshine-api  # 先重启
python3.11 migrations/xxx.py  # 后迁移（可能导致服务启动失败）
```

---

## 📊 部署检查表（打印版）

```
□ 本地代码已提交并推送到 GitHub
□ 服务器已拉取最新代码
□ 数据库已备份（如有变更）
□ 数据库迁移已执行（如有变更）
□ 服务已重启
□ 服务状态正常（active running）
□ 本地健康检查通过（localhost:8000/health）
□ 外网健康检查通过（https://cshine.xuyucloud.com/health）
□ 小程序配置使用 HTTPS 域名
□ 小程序已重新上传到体验版
□ 体验版功能测试通过
```

---

## 🎓 经验总结

### 本次部署（v0.5.5 → v0.5.18）遇到的所有问题

1. ❌ 虚拟环境路径错误 → ✅ 修正为项目根目录
2. ❌ Python 命令错误 → ✅ 使用 `python3.11`
3. ❌ 数据库连接配置错误 → ✅ 使用 `DATABASE_URL` 解析
4. ❌ 代码未推送到远程 → ✅ 养成 `push` 习惯
5. ❌ 服务未重启 → ✅ 明确重启流程
6. ❌ 小程序使用 HTTP → ✅ 改用 HTTPS 域名

### 核心教训

1. **部署是一个完整的流程**，不是单个步骤
2. **本地环境 ≠ 服务器环境**，配置要适配
3. **验证每一步**，不要假设某步已完成
4. **文档化经验**，避免重复犯错
5. **自动化脚本**，减少人为错误

---

**版本**: v1.0  
**更新日期**: 2025-11-12  
**适用项目**: Cshine  
**维护者**: AI Assistant

---

**Let Your Ideas Shine. ✨**

