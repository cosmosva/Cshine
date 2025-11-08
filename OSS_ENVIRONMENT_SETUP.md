# 📦 OSS 环境隔离配置指南

## 🎯 问题说明

**当前状况：** 开发和生产环境共用同一个 OSS Bucket

```
┌─────────────┐
│ 本地开发    │ ──┐
└─────────────┘   │
                  ├──→  cshine-audio (同一个bucket)
┌─────────────┐   │
│ 生产环境    │ ──┘
└─────────────┘
```

**潜在风险：**
- ❌ 测试数据污染生产数据
- ❌ 误删生产环境文件
- ❌ 费用无法区分
- ❌ 安全隐患

---

## ✅ 推荐方案

### 方案 A：使用不同的 Bucket（最佳，强烈推荐）

```
┌─────────────┐
│ 本地开发    │ ──→  cshine-audio-dev
└─────────────┘

┌─────────────┐
│ 生产环境    │ ──→  cshine-audio (或 cshine-audio-prod)
└─────────────┘
```

**优势：**
- ✅ 完全隔离，最安全
- ✅ 可以独立配置权限
- ✅ 费用清晰可见
- ✅ 可以随时清空开发 bucket

**成本：**
- 每个 bucket 都有最低存储费用
- 但开发 bucket 可以定期清理，成本很低

---

### 方案 B：同一 Bucket 不同路径前缀（次选）

```
cshine-audio/
  ├── dev/audio/      ← 开发环境
  └── prod/audio/     ← 生产环境
```

**优势：**
- ✅ 只需一个 bucket
- ✅ 成本更低

**劣势：**
- ⚠️ 隔离度不够高
- ⚠️ 仍有误操作风险

---

### 方案 C：开发环境使用本地存储（最经济）

```
┌─────────────┐
│ 本地开发    │ ──→  ./uploads/ (本地文件夹)
└─────────────┘

┌─────────────┐
│ 生产环境    │ ──→  cshine-audio (OSS)
└─────────────┘
```

**优势：**
- ✅ 开发完全免费
- ✅ 不需要配置 OSS 密钥
- ✅ 测试更快

**劣势：**
- ⚠️ 无法测试 OSS 相关功能
- ⚠️ 本地文件占用磁盘空间

---

## 🚀 实施步骤

### 推荐：方案 A（不同 Bucket）

#### 1. 创建开发 Bucket

**登录阿里云 OSS 控制台：**
```
https://oss.console.aliyun.com/
  → 创建 Bucket
  → Bucket 名称: cshine-audio-dev
  → 区域: 华南1（深圳）或 华南3（广州）
  → 存储类型: 标准存储
  → 读写权限: 公共读（如果需要直接访问）或 私有（更安全）
  → 确认创建
```

#### 2. 配置本地环境

**编辑 `backend/.env` 文件：**
```bash
# 开发环境配置
OSS_BUCKET_NAME=cshine-audio-dev

# 其他 OSS 配置保持不变
ALIBABA_CLOUD_ACCESS_KEY_ID=your_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_key_secret
OSS_ENDPOINT=oss-cn-guangzhou.aliyuncs.com
```

#### 3. 配置生产环境

**编辑生产服务器的 `.env` 文件：**
```bash
# 生产环境配置
OSS_BUCKET_NAME=cshine-audio

# 其他配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_key_secret
OSS_ENDPOINT=oss-cn-guangzhou.aliyuncs.com
```

#### 4. 验证配置

**本地测试：**
```bash
cd backend
python -c "from config import settings; print(f'OSS Bucket: {settings.OSS_BUCKET_NAME}')"

# 应该输出：OSS Bucket: cshine-audio-dev
```

**生产环境测试：**
```bash
ssh user@your-server
cd /path/to/backend
source venv/bin/activate
python -c "from config import settings; print(f'OSS Bucket: {settings.OSS_BUCKET_NAME}')"

# 应该输出：OSS Bucket: cshine-audio
```

---

### 经济：方案 C（本地存储 + OSS）

#### 1. 配置本地使用本地存储

**编辑 `backend/.env` 文件：**
```bash
# 使用本地存储
STORAGE_TYPE=local
UPLOAD_DIR=./uploads

# OSS 配置留空或注释掉（不使用）
# OSS_BUCKET_NAME=
# ALIBABA_CLOUD_ACCESS_KEY_ID=
# ALIBABA_CLOUD_ACCESS_KEY_SECRET=
```

#### 2. 配置生产使用 OSS

**编辑生产服务器的 `.env` 文件：**
```bash
# 使用 OSS 存储
STORAGE_TYPE=oss

# OSS 配置
OSS_BUCKET_NAME=cshine-audio
ALIBABA_CLOUD_ACCESS_KEY_ID=your_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_key_secret
OSS_ENDPOINT=oss-cn-guangzhou.aliyuncs.com
```

#### 3. 代码已支持动态切换

`config.py` 中已经有 `STORAGE_TYPE` 配置，后端代码需要根据这个配置动态选择存储方式。

---

## 📊 成本对比

### 方案 A：不同 Bucket

**开发 Bucket（cshine-audio-dev）：**
```
存储费用：￥0.12/GB/月
下载流量：￥0.50/GB（内网免费）
请求次数：￥0.01/万次

预估：
- 存储 1GB 测试数据：￥0.12/月
- 每月可以清空，几乎免费
```

**生产 Bucket（cshine-audio）：**
```
根据实际用户使用量计费
```

**总成本：** 每月增加不到 ￥1

---

### 方案 C：本地 + OSS

**开发：** 完全免费（使用本地磁盘）

**生产：** 按实际使用计费

**总成本：** 开发阶段 ￥0

---

## 🛡️ 安全最佳实践

### 1. 使用不同的 AccessKey

**理想情况：**
```
开发环境：使用 RAM 子账号，只有 cshine-audio-dev 权限
生产环境：使用 RAM 子账号，只有 cshine-audio 权限
```

**创建 RAM 子账号：**
```
阿里云控制台
  → 访问控制 (RAM)
  → 用户
  → 创建用户
  → 勾选"编程访问"
  → 分配权限：AliyunOSSFullAccess（或自定义策略）
  → 保存 AccessKey ID 和 Secret
```

### 2. 定期清理开发 Bucket

**设置生命周期规则：**
```
OSS 控制台
  → 选择 cshine-audio-dev
  → 基础设置
  → 生命周期
  → 创建规则：
      - 前缀：audio/
      - 有效期：7 天后删除
```

这样测试文件会自动清理，不会累积。

### 3. 开发 Bucket 设置防误删

**启用版本控制：**
```
OSS 控制台
  → cshine-audio-dev
  → 基础设置
  → 版本控制：开启
```

误删可以恢复（但会增加存储成本）。

---

## 📝 配置文件对比

### 开发环境 `.env`

```bash
# 应用配置
APP_NAME=Cshine API
DEBUG=true

# 数据库（本地）
DATABASE_URL=sqlite:///./cshine.db

# OSS（开发 bucket）
STORAGE_TYPE=local  # 或 oss
OSS_BUCKET_NAME=cshine-audio-dev
ALIBABA_CLOUD_ACCESS_KEY_ID=LTAI5t...（开发用）
ALIBABA_CLOUD_ACCESS_KEY_SECRET=xxx...

# 微信（测试号）
WECHAT_APPID=wx68cb1f3f6a2bcf17
WECHAT_SECRET=73a2781f...
```

### 生产环境 `.env`

```bash
# 应用配置
APP_NAME=Cshine API
DEBUG=false

# 数据库（PostgreSQL 或远程数据库）
DATABASE_URL=postgresql://user:pass@localhost/cshine

# OSS（生产 bucket）
STORAGE_TYPE=oss
OSS_BUCKET_NAME=cshine-audio
ALIBABA_CLOUD_ACCESS_KEY_ID=LTAI5t...（生产用）
ALIBABA_CLOUD_ACCESS_KEY_SECRET=xxx...

# 微信（正式账号）
WECHAT_APPID=wx68cb1f3f6a2bcf17
WECHAT_SECRET=73a2781f...
```

---

## 🔍 验证清单

### 本地开发环境

```bash
# 1. 检查配置
python -c "from config import settings; \
    print(f'Bucket: {settings.OSS_BUCKET_NAME}'); \
    print(f'Storage: {settings.STORAGE_TYPE}')"

# 2. 上传测试文件
# 通过小程序上传音频
# 检查文件去了哪里：
# - local：查看 ./uploads/ 目录
# - oss：登录 OSS 控制台查看 cshine-audio-dev
```

### 生产环境

```bash
# SSH 到服务器
ssh user@your-server

# 1. 检查配置
cd /path/to/backend
python -c "from config import settings; \
    print(f'Bucket: {settings.OSS_BUCKET_NAME}'); \
    print(f'Storage: {settings.STORAGE_TYPE}')"

# 2. 上传测试
# 使用正式版小程序上传
# 登录 OSS 控制台查看 cshine-audio
```

---

## 🤔 常见问题

### Q1: 我已经在共用 bucket 里有文件了怎么办？

**A: 可以迁移或不动**

**不迁移（简单）：**
```
现有文件：继续在 cshine-audio
新上传：  根据环境去不同 bucket
```

**迁移（彻底）：**
```bash
# 1. 区分哪些是测试数据，哪些是真实数据
# 2. 使用 ossutil 批量复制
ossutil cp oss://cshine-audio/test/ oss://cshine-audio-dev/ --recursive
# 3. 验证后删除原文件
```

---

### Q2: 开发 bucket 要和生产一样的权限吗？

**A: 不需要，开发可以更宽松**

**开发 bucket：**
- 公共读（方便调试）
- 允许匿名访问（可选）
- 不需要 CDN
- 生命周期：7天自动删除

**生产 bucket：**
- 私有（更安全）
- 需要签名访问
- 配置 CDN 加速
- 不自动删除

---

### Q3: 切换 bucket 后，旧链接会失效吗？

**A: 会的！**

如果你改变了 bucket 名称：
```
旧链接：https://cshine-audio.oss-cn-guangzhou.aliyuncs.com/audio/xxx.wav
新链接：https://cshine-audio-dev.oss-cn-guangzhou.aliyuncs.com/audio/xxx.wav
```

**解决方案：**
- 本地开发数据库的链接失效无所谓（测试数据）
- 生产环境不要改 bucket 名称
- 如果必须改，需要批量更新数据库中的 URL

---

### Q4: 我想省钱，能只用本地存储吗？

**A: 可以！但有限制**

**适合场景：**
```
✅ 纯本地开发测试
✅ 数据量小（< 10GB）
✅ 不需要跨设备访问
```

**不适合：**
```
❌ 真机测试（手机无法访问你的电脑）
❌ 团队协作（其他人看不到你的文件）
❌ CI/CD 自动化测试
```

**推荐：**
```
开发早期：本地存储（免费）
联调阶段：切换到 OSS dev bucket
上线前：  确保生产用 OSS
```

---

## 🎯 我的建议

### 根据你的情况

**当前阶段：开发测试**
```
推荐：方案 C（本地存储）

理由：
✅ 完全免费
✅ 测试更快
✅ 不需要配置 OSS
✅ 你目前是一个人开发
```

**配置：**
```bash
# backend/.env
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
```

---

**准备发布阶段：**
```
推荐：方案 A（不同 Bucket）

理由：
✅ 生产数据隔离
✅ 可以放心测试
✅ 成本几乎为零（dev bucket 定期清理）
```

**配置：**
```bash
# 本地 .env
STORAGE_TYPE=oss
OSS_BUCKET_NAME=cshine-audio-dev

# 生产 .env
STORAGE_TYPE=oss
OSS_BUCKET_NAME=cshine-audio
```

---

## 📋 行动计划

### 立即行动（推荐）

```bash
# 1. 修改本地配置，使用本地存储
cd backend
echo "STORAGE_TYPE=local" >> .env
echo "UPLOAD_DIR=./uploads" >> .env

# 2. 重启后端
python main.py

# 3. 测试上传
# 上传文件后检查 ./uploads/ 目录
ls -lh uploads/

# ✅ 现在开发完全免费，不会污染 OSS！
```

### 上线前行动

```bash
# 1. 阿里云创建 cshine-audio-dev bucket
# 2. 获取 RAM 子账号密钥
# 3. 本地配置切换到 OSS
echo "STORAGE_TYPE=oss" >> .env
echo "OSS_BUCKET_NAME=cshine-audio-dev" >> .env

# 4. 生产环境保持原配置
# OSS_BUCKET_NAME=cshine-audio
```

---

## ✨ 总结

| 方案 | 成本 | 安全性 | 复杂度 | 推荐场景 |
|-----|------|--------|--------|----------|
| **不同 Bucket** | 低 | ⭐⭐⭐⭐⭐ | 中 | 上线后 |
| **同 Bucket 不同路径** | 最低 | ⭐⭐⭐ | 低 | 小团队 |
| **本地 + OSS** | 开发免费 | ⭐⭐⭐⭐ | 低 | **当前推荐** |

**我的建议：**
1. **现在**：用本地存储（免费、快速）
2. **上线前**：切换到不同 Bucket（安全、隔离）
3. **上线后**：定期清理 dev bucket（省钱）

有任何问题随时问我！🚀

