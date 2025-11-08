# 🎯 开发环境 OSS 配置指南

## ✅ 你已完成

- [x] 在阿里云创建了 `cshine-audio-dev` bucket
- [x] 设置为公共读权限

## 📝 下一步：配置本地环境

### 1. 编辑 `.env` 文件

```bash
cd /Users/cosmos_pro/Documents/文稿\ -\ cosmos/CODE/CP/Cshine/backend

# 如果没有 .env 文件，从模板创建
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

### 2. 修改 OSS 配置

在 `.env` 文件中找到并修改：

```bash
# ============================================
# 文件存储配置
# ============================================
STORAGE_TYPE=oss  # 使用 OSS 存储

# ============================================
# 阿里云 OSS 配置
# ============================================
OSS_BUCKET_NAME=cshine-audio-dev  # 👈 开发环境用这个
OSS_ENDPOINT=oss-cn-guangzhou.aliyuncs.com

# 阿里云访问密钥
ALIBABA_CLOUD_ACCESS_KEY_ID=你的AccessKeyId
ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的AccessKeySecret
```

**⚠️ 重要：** 确保填写正确的阿里云 AccessKey！

---

## 🧪 测试配置

### 步骤 1：验证配置

```bash
cd backend
python -c "from config import settings; \
    print('=== 当前配置 ==='); \
    print(f'存储类型: {settings.STORAGE_TYPE}'); \
    print(f'OSS Bucket: {settings.OSS_BUCKET_NAME}'); \
    print(f'OSS Endpoint: {settings.OSS_ENDPOINT}'); \
    print(f'OSS Base URL: {settings.oss_base_url}')"
```

**期望输出：**
```
=== 当前配置 ===
存储类型: oss
OSS Bucket: cshine-audio-dev
OSS Endpoint: oss-cn-guangzhou.aliyuncs.com
OSS Base URL: https://cshine-audio-dev.oss-cn-guangzhou.aliyuncs.com
```

### 步骤 2：测试 OSS 连接

```bash
python -c "from app.utils.oss import check_oss_connection; \
    result = check_oss_connection(); \
    print('✅ OSS 连接成功' if result else '❌ OSS 连接失败')"
```

### 步骤 3：启动后端并测试上传

```bash
# 启动后端
python main.py
```

**在另一个终端查看日志：**
```bash
tail -f logs/cshine.log
```

**通过小程序上传音频文件，观察：**

1. **控制台输出：**
```
开始上传文件到 OSS: audio/20241108/xxx-xxx-xxx.wav
✅ 文件上传成功: https://cshine-audio-dev.oss-cn-guangzhou.aliyuncs.com/audio/20241108/xxx.wav
```

2. **阿里云 OSS 控制台：**
```
https://oss.console.aliyun.com/
  → 选择 cshine-audio-dev
  → 文件管理
  → 应该能看到 audio/20241108/ 目录下的文件
```

3. **访问文件（公共读）：**
```bash
# 直接在浏览器打开返回的 URL
https://cshine-audio-dev.oss-cn-guangzhou.aliyuncs.com/audio/20241108/xxx.wav

# 应该能直接播放或下载
```

---

## 🔄 环境对比

### 开发环境（你当前）

```bash
# .env
STORAGE_TYPE=oss
OSS_BUCKET_NAME=cshine-audio-dev

# 效果
上传 → https://cshine-audio-dev.oss-cn-guangzhou.aliyuncs.com/audio/xxx.wav
```

### 生产环境（线上服务器）

```bash
# .env
STORAGE_TYPE=oss
OSS_BUCKET_NAME=cshine-audio

# 效果
上传 → https://cshine-audio.oss-cn-guangzhou.aliyuncs.com/audio/xxx.wav
```

### 现在的隔离效果

```
┌─────────────┐
│ 本地开发    │ ──→  cshine-audio-dev  ✅
└─────────────┘       (测试文件)

┌─────────────┐
│ 线上生产    │ ──→  cshine-audio      ✅
└─────────────┘       (用户真实文件)

✅ 完全隔离，互不影响！
```

---

## 🛠️ 常见问题

### Q1: AccessKey 在哪里获取？

**A: 阿里云 RAM 控制台**

```
1. 登录阿里云控制台：https://ram.console.aliyun.com/
2. 左侧菜单 → 身份管理 → 用户
3. 找到你的用户 → 创建 AccessKey
4. 保存 AccessKey ID 和 Secret（只显示一次！）
```

**⚠️ 安全建议：** 使用 RAM 子账号，只授予 OSS 权限

---

### Q2: 我没有 .env 文件怎么办？

**A: 创建一个**

```bash
cd backend

# 方法 1：复制模板
cp .env.example .env

# 方法 2：手动创建
cat > .env << 'EOF'
# OSS 配置
STORAGE_TYPE=oss
OSS_BUCKET_NAME=cshine-audio-dev
OSS_ENDPOINT=oss-cn-guangzhou.aliyuncs.com
ALIBABA_CLOUD_ACCESS_KEY_ID=你的key
ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的secret

# 微信配置
WECHAT_APPID=wx68cb1f3f6a2bcf17
WECHAT_SECRET=73a2781f1c83d81f883f9957a02f8e01
EOF

# 编辑填入实际值
nano .env
```

---

### Q3: 报错 "AccessKey ID not found"

**A: AccessKey 配置错误**

```bash
# 检查配置
python -c "from config import settings; \
    print(f'AccessKey ID: {settings.ALIBABA_CLOUD_ACCESS_KEY_ID[:10]}...')"

# 如果显示空或错误，重新配置 .env
```

---

### Q4: 报错 "NoSuchBucket"

**A: Bucket 不存在或名称错误**

```bash
# 1. 确认 Bucket 名称
python -c "from config import settings; print(settings.OSS_BUCKET_NAME)"

# 2. 登录 OSS 控制台确认 Bucket 是否存在
# https://oss.console.aliyun.com/

# 3. 确认 Bucket 和 Endpoint 匹配
# 例如：Bucket 在广州，Endpoint 就要用 oss-cn-guangzhou.aliyuncs.com
```

---

### Q5: 文件上传成功，但无法访问

**A: 权限问题**

```
OSS 控制台
  → 选择 cshine-audio-dev
  → 权限管理
  → 读写权限：确认是"公共读"
```

如果是私有 Bucket，需要使用签名 URL：
```python
from app.utils.oss import get_signed_url
signed_url = get_signed_url(oss_url)
```

---

## 📊 配置检查清单

配置前：
- [ ] 已在阿里云创建 `cshine-audio-dev` bucket
- [ ] 已获取阿里云 AccessKey ID 和 Secret
- [ ] Bucket 设置为公共读（或私有 + 签名访问）

配置中：
- [ ] 创建或编辑 `backend/.env` 文件
- [ ] 设置 `STORAGE_TYPE=oss`
- [ ] 设置 `OSS_BUCKET_NAME=cshine-audio-dev`
- [ ] 填写 AccessKey ID 和 Secret
- [ ] 确认 Endpoint 正确

测试：
- [ ] 运行配置验证脚本（看到正确的 bucket 名称）
- [ ] 运行 OSS 连接测试（显示连接成功）
- [ ] 启动后端服务
- [ ] 通过小程序上传测试文件
- [ ] 在 OSS 控制台看到上传的文件
- [ ] 能够访问文件 URL（公共读）

---

## 🎉 完成后的效果

### 本地开发

```bash
# 上传文件
POST /api/v1/upload/audio

# 返回
{
  "url": "https://cshine-audio-dev.oss-cn-guangzhou.aliyuncs.com/audio/20241108/xxx.wav",
  "file_id": "xxx-xxx-xxx"
}

# ✅ 文件存在开发 bucket，不会污染生产环境
```

### 生产环境

```bash
# 上传文件
POST /api/v1/upload/audio

# 返回
{
  "url": "https://cshine-audio.oss-cn-guangzhou.aliyuncs.com/audio/20241108/xxx.wav",
  "file_id": "xxx-xxx-xxx"
}

# ✅ 文件存在生产 bucket，与开发完全隔离
```

---

## 🚀 快速开始

```bash
# 1. 进入后端目录
cd /Users/cosmos_pro/Documents/文稿\ -\ cosmos/CODE/CP/Cshine/backend

# 2. 编辑 .env（如果没有就创建）
nano .env

# 3. 添加配置
# STORAGE_TYPE=oss
# OSS_BUCKET_NAME=cshine-audio-dev
# ALIBABA_CLOUD_ACCESS_KEY_ID=你的key
# ALIBABA_CLOUD_ACCESS_KEY_SECRET=你的secret

# 4. 验证配置
python -c "from config import settings; print(f'Bucket: {settings.OSS_BUCKET_NAME}')"

# 5. 测试连接
python -c "from app.utils.oss import check_oss_connection; check_oss_connection()"

# 6. 启动服务
python main.py

# ✅ 开始测试上传！
```

---

## 📞 遇到问题？

如果配置过程中遇到任何问题，随时告诉我：

1. **具体的错误信息**（完整的 traceback）
2. **你的配置**（AccessKey 等敏感信息可以隐藏）
3. **在哪一步卡住了**

我会帮你解决！🚀

