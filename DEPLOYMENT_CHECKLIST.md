# 📋 线上部署快速清单

## 🎯 部署概览

**功能**: 文件上传 + 知识库管理  
**版本**: v1.1.0  
**影响**: 数据库结构变更 + 新增 API

---

## ⚡ 快速部署（5 分钟）

### 本地测试已完成 ✅

如果本地测试通过，执行以下步骤：

```bash
# 1. 连接到服务器
ssh your-server

# 2. 进入项目目录
cd /path/to/Cshine

# 3. 运行一键部署脚本
./backend/deploy/deploy_upload_feature.sh
```

就这么简单！脚本会自动完成：
- ✅ 数据库备份
- ✅ 代码更新
- ✅ 数据库迁移
- ✅ 服务重启
- ✅ 健康检查

---

## 📝 详细步骤（手动部署）

### 1️⃣ 服务器端部署

#### SSH 连接
```bash
ssh username@your-server-ip
```

#### 备份数据库（重要！）
```bash
cd /path/to/Cshine/backend
cp cshine.db cshine.db.backup.$(date +%Y%m%d_%H%M%S)
```

#### 更新代码
```bash
git pull origin main
```

#### 运行迁移
```bash
cd backend
source venv/bin/activate
python migrations/add_folders_and_folder_id.py
```

#### 重启服务

**方式 A: systemd**
```bash
sudo systemctl restart cshine
sudo systemctl status cshine
```

**方式 B: 手动**
```bash
pkill -f "python.*main.py"
nohup python main.py > server.log 2>&1 &
```

#### 验证部署
```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

### 2️⃣ 小程序端部署

#### 本地准备
1. 在微信开发者工具中编译
2. 真机调试测试功能
3. 确认无误

#### 上传代码
1. 点击 "上传"
2. 版本号：**1.1.0**
3. 备注：**新增文件上传和知识库管理功能**

#### 提交审核
1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 开发管理 → 版本管理 → 开发版本
3. 点击 "提交审核"
4. 填写功能说明（见下方模板）

#### 审核说明模板
```
【功能更新】
1. 新增文件上传功能
   - 支持音频文件上传（mp3/m4a/wav）
   - 实时显示上传进度
   
2. 新增知识库管理功能
   - 创建和管理知识库
   - 按知识库分类会议
   
3. 优化会议列表
   - 支持按知识库筛选
   
【测试路径】
1. 进入"知识库"页面
2. 点击右上角"+"按钮
3. 选择"上传文件"测试上传功能
4. 选择"新建知识库"测试管理功能
```

#### 域名配置（如未配置）
在微信公众平台 → 开发 → 开发设置 → 服务器域名：
- **request**: `https://your-domain.com`
- **uploadFile**: `https://your-oss-bucket.oss-cn-region.aliyuncs.com`

---

## 🔍 验证清单

### 后端验证 ✅

```bash
# 健康检查
curl http://localhost:8000/health
# 预期: {"status":"healthy"}

# API 文档
curl -I http://localhost:8000/docs
# 预期: 200 OK

# 查看日志
tail -50 /path/to/backend/logs/cshine.log
# 无错误信息

# 检查数据库
sqlite3 cshine.db "SELECT COUNT(*) FROM folders;"
# 预期: 返回数字（0 或更多）
```

### 小程序验证 ✅

- [ ] 小程序可正常打开
- [ ] 登录功能正常
- [ ] 原有功能正常（闪记、会议列表）
- [ ] 点击 "+" 按钮显示菜单
- [ ] 上传文件功能正常
- [ ] 知识库创建正常
- [ ] 列表筛选正常

---

## 🚨 回滚方案

### 后端回滚
```bash
# 方式 1: 使用回滚脚本
cd /path/to/Cshine
./backend/deploy/rollback_upload_feature.sh

# 方式 2: 手动回滚
cd backend
sudo systemctl stop cshine
cp cshine.db.backup.YYYYMMDD_HHMMSS cshine.db
sudo systemctl start cshine
```

### 小程序回滚
1. 登录微信公众平台
2. 版本管理 → 线上版本
3. 点击 "版本回退"

---

## 📊 灰度发布建议

### 第一阶段（5% - 1天）
- 小范围用户测试
- 密切监控错误日志
- 收集用户反馈

### 第二阶段（20% - 2天）
- 扩大测试范围
- 验证稳定性

### 第三阶段（100%）
- 全量发布

---

## 🆘 问题排查

### 问题 1: 数据库迁移失败
```bash
# 查看错误
python migrations/add_folders_and_folder_id.py

# 检查表是否存在
sqlite3 cshine.db "PRAGMA table_info(folders);"
```

### 问题 2: 服务启动失败
```bash
# 查看日志
tail -100 /path/to/backend/logs/cshine.log

# 检查端口
lsof -i :8000

# 手动启动调试
cd backend
source venv/bin/activate
python main.py
```

### 问题 3: 小程序上传失败
1. 检查服务器 OSS 配置
2. 检查小程序域名白名单
3. 查看后端日志中的错误

---

## 📞 紧急联系

部署遇到问题：
1. 立即执行回滚
2. 保存错误日志
3. 联系技术支持

---

## 📚 相关文档

- **详细部署指南**: [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- **实现总结**: [UPLOAD_FEATURE_IMPLEMENTATION.md](./UPLOAD_FEATURE_IMPLEMENTATION.md)
- **开发计划**: [UPLOAD_FEATURE_PLAN.md](./UPLOAD_FEATURE_PLAN.md)

---

## ✅ 部署记录

| 日期 | 环境 | 操作人 | 结果 | 备注 |
|------|------|--------|------|------|
| YYYY-MM-DD | 测试环境 | - | ✅ | 本地测试通过 |
| YYYY-MM-DD | 生产环境 | - | - | 待部署 |

---

**更新时间**: 2025-11-09  
**负责人**: DevOps Team

