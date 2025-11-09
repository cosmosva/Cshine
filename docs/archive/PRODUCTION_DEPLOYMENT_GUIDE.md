# 🚀 线上部署更新指南

## 📋 部署前检查清单

### 本地验证
- [x] 数据库迁移脚本已测试
- [x] 后端服务本地运行正常
- [x] API 接口测试通过
- [ ] 小程序本地编译通过
- [ ] 真机调试测试通过
- [ ] 所有功能测试完成

### 代码准备
- [ ] 所有代码已提交到 Git
- [ ] 创建版本标签（如 v1.1.0）
- [ ] 更新 CHANGELOG.md

---

## 🖥️ 后端部署步骤

### 方式一：使用部署脚本（推荐）

#### 1. 连接到服务器
```bash
ssh your-username@your-server-ip
# 或使用配置的别名
ssh cshine-server
```

#### 2. 进入项目目录
```bash
cd /path/to/Cshine/backend
```

#### 3. 备份数据库（重要！）
```bash
# 备份当前数据库
cp cshine.db cshine.db.backup.$(date +%Y%m%d_%H%M%S)

# 或使用完整备份脚本
./deploy/backup_db.sh
```

#### 4. 拉取最新代码
```bash
git pull origin main
```

#### 5. 运行数据库迁移
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行迁移脚本
python migrations/add_folders_and_folder_id.py
```

预期输出：
```
✅ 创建 folders 表成功
✅ 创建 folders 表索引成功
✅ 添加 folder_id 字段到 meetings 表成功
✅ 数据库迁移完成！
```

#### 6. 重启后端服务

**如果使用 systemd**：
```bash
sudo systemctl restart cshine
sudo systemctl status cshine
```

**如果使用 PM2**：
```bash
pm2 restart cshine
pm2 logs cshine --lines 50
```

**如果是手动运行**：
```bash
# 停止旧进程
pkill -f "python.*main.py"

# 启动新进程
nohup python main.py > server.log 2>&1 &
echo $! > server.pid
```

#### 7. 验证服务状态
```bash
# 检查健康状态
curl http://localhost:8000/health

# 查看日志
tail -50 logs/cshine.log

# 检查新 API 端点
curl http://localhost:8000/docs
```

---

### 方式二：使用一键部署脚本

创建部署脚本 `deploy/deploy_upload_feature.sh`：

```bash
#!/bin/bash
set -e

echo "🚀 开始部署上传功能..."

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 备份数据库
echo -e "${YELLOW}1. 备份数据库...${NC}"
BACKUP_FILE="cshine.db.backup.$(date +%Y%m%d_%H%M%S)"
cp cshine.db "$BACKUP_FILE"
echo -e "${GREEN}✅ 数据库已备份到: $BACKUP_FILE${NC}"

# 2. 拉取代码
echo -e "${YELLOW}2. 拉取最新代码...${NC}"
git pull origin main
echo -e "${GREEN}✅ 代码更新完成${NC}"

# 3. 激活虚拟环境
echo -e "${YELLOW}3. 激活虚拟环境...${NC}"
source venv/bin/activate

# 4. 运行数据库迁移
echo -e "${YELLOW}4. 运行数据库迁移...${NC}"
python migrations/add_folders_and_folder_id.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库迁移成功${NC}"
else
    echo -e "${RED}❌ 数据库迁移失败，恢复备份...${NC}"
    cp "$BACKUP_FILE" cshine.db
    exit 1
fi

# 5. 重启服务
echo -e "${YELLOW}5. 重启后端服务...${NC}"
sudo systemctl restart cshine

# 等待服务启动
sleep 3

# 6. 验证服务
echo -e "${YELLOW}6. 验证服务状态...${NC}"
HEALTH_CHECK=$(curl -s http://localhost:8000/health | grep -o '"status":"healthy"')

if [ ! -z "$HEALTH_CHECK" ]; then
    echo -e "${GREEN}✅ 服务运行正常${NC}"
    echo ""
    echo "🎉 部署成功！"
    echo ""
    echo "📝 新增 API 端点:"
    echo "  - GET  /api/v1/upload/oss-signature"
    echo "  - POST /api/v1/folders"
    echo "  - GET  /api/v1/folders"
    echo "  - PUT  /api/v1/folders/{id}"
    echo "  - DELETE /api/v1/folders/{id}"
    echo ""
    echo "🌐 API 文档: http://your-domain.com/docs"
else
    echo -e "${RED}❌ 服务启动失败，查看日志：${NC}"
    tail -20 logs/cshine.log
    exit 1
fi
```

使用方法：
```bash
cd /path/to/Cshine/backend
chmod +x deploy/deploy_upload_feature.sh
./deploy/deploy_upload_feature.sh
```

---

## 📱 小程序端部署步骤

### 1. 本地最终测试
在微信开发者工具中：
- [ ] 编译无错误
- [ ] 真机调试功能正常
- [ ] 上传功能测试通过
- [ ] 知识库功能测试通过

### 2. 更新版本号
编辑 `app.json` 或 `project.config.json`：
```json
{
  "version": "1.1.0",
  "description": "新增：文件上传和知识库管理功能"
}
```

### 3. 上传代码
在微信开发者工具中：
1. 点击右上角 "上传"
2. 填写版本信息：
   - **版本号**: 1.1.0
   - **项目备注**: 新增文件上传和知识库管理功能
   
### 4. 提交审核
登录 [微信公众平台](https://mp.weixin.qq.com/)：

1. **进入版本管理**
   - 开发管理 → 版本管理 → 开发版本

2. **提交审核**
   - 点击 "提交审核"
   - 填写审核信息：
     ```
     【功能更新】
     1. 新增文件上传功能，支持音频文件上传
     2. 新增知识库管理功能，可创建和管理知识库
     3. 优化会议列表，支持按知识库筛选
     
     【测试账号】
     账号: test@example.com
     密码: Test123456
     
     【测试路径】
     1. 进入"知识库"页面
     2. 点击右上角"+"按钮
     3. 选择"上传文件"或"新建知识库"
     ```

3. **配置服务器域名**（如果还没配置）
   - 开发 → 开发设置 → 服务器域名
   - **request 合法域名**: `https://your-domain.com`
   - **uploadFile 合法域名**: `https://your-oss-bucket.oss-cn-region.aliyuncs.com`

4. **等待审核**
   - 审核时间：通常 1-7 个工作日
   - 可在"版本管理"中查看审核状态

### 5. 审核通过后发布
- 审核通过后，点击 "发布"
- 设置灰度比例（可选，建议先 5% → 20% → 100%）

---

## 🔄 灰度发布策略（推荐）

### 后端灰度
如果服务器有负载均衡，可以分批更新：
1. 更新 1 台服务器，观察 30 分钟
2. 无问题后更新其余服务器

### 小程序灰度
1. **第一阶段（5%）**: 发布后选择 5% 灰度
   - 观察 1-2 天
   - 监控错误日志
   - 收集用户反馈

2. **第二阶段（20%）**: 无问题后提升到 20%
   - 观察 1-2 天

3. **第三阶段（100%）**: 全量发布

---

## 📊 监控检查

### 后端监控
```bash
# 实时查看日志
tail -f logs/cshine.log

# 查看错误日志
grep -i error logs/cshine.log | tail -20

# 检查进程
ps aux | grep python

# 检查内存使用
free -h

# 检查磁盘空间
df -h
```

### 数据库检查
```bash
# 连接数据库
sqlite3 cshine.db

# 检查 folders 表
SELECT COUNT(*) FROM folders;

# 检查 meetings 表的 folder_id 字段
SELECT COUNT(*) FROM meetings WHERE folder_id IS NOT NULL;
```

### API 监控
```bash
# 测试新端点
curl -X GET "http://your-domain.com/api/v1/folders" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看 API 响应时间
curl -w "@-" -o /dev/null -s "http://your-domain.com/health" <<'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
EOF
```

---

## 🚨 回滚方案

### 后端回滚

#### 方案一：代码回滚
```bash
# 1. 回滚到上一个版本
git log --oneline  # 查看提交记录
git checkout <上一个版本的commit-hash>

# 2. 恢复数据库
cp cshine.db.backup.YYYYMMDD_HHMMSS cshine.db

# 3. 重启服务
sudo systemctl restart cshine
```

#### 方案二：数据库回滚（如果只是数据库问题）
```bash
# 1. 停止服务
sudo systemctl stop cshine

# 2. 恢复数据库备份
cp cshine.db.backup.YYYYMMDD_HHMMSS cshine.db

# 3. 启动服务
sudo systemctl start cshine
```

#### 方案三：使用回滚脚本
```bash
#!/bin/bash
# deploy/rollback.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "用法: ./rollback.sh <backup_file>"
    echo "可用备份:"
    ls -lh cshine.db.backup.*
    exit 1
fi

echo "⚠️  准备回滚到: $BACKUP_FILE"
read -p "确认回滚? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo "停止服务..."
    sudo systemctl stop cshine
    
    echo "恢复数据库..."
    cp "$BACKUP_FILE" cshine.db
    
    echo "启动服务..."
    sudo systemctl start cshine
    
    echo "✅ 回滚完成"
else
    echo "❌ 取消回滚"
fi
```

### 小程序回滚
1. 登录微信公众平台
2. 版本管理 → 线上版本
3. 点击 "版本回退"
4. 选择要回退的版本
5. 确认回退

---

## 📝 部署后验证清单

### 后端验证
- [ ] 服务健康检查通过
- [ ] API 文档可访问
- [ ] 数据库连接正常
- [ ] OSS 连接正常
- [ ] 新 API 端点可访问
- [ ] 旧 API 端点正常工作
- [ ] 日志无错误

### 小程序验证
- [ ] 小程序可正常打开
- [ ] 登录功能正常
- [ ] 原有功能正常（闪记、会议列表等）
- [ ] 上传功能正常
- [ ] 知识库功能正常
- [ ] 文件选择正常
- [ ] 上传进度正常
- [ ] 列表筛选正常

### 用户体验验证
- [ ] 界面显示正常
- [ ] 交互流畅
- [ ] 错误提示友好
- [ ] 加载速度正常

---

## 🔧 常见问题处理

### 问题 1: 数据库迁移失败
**症状**: 运行迁移脚本报错
**解决**:
```bash
# 查看具体错误
python migrations/add_folders_and_folder_id.py

# 如果表已存在，手动检查
sqlite3 cshine.db "PRAGMA table_info(folders);"
sqlite3 cshine.db "PRAGMA table_info(meetings);"

# 如果需要，手动执行 SQL
sqlite3 cshine.db < migrations/manual_fix.sql
```

### 问题 2: 服务启动失败
**症状**: systemctl status 显示 failed
**解决**:
```bash
# 查看详细错误
journalctl -u cshine -n 50

# 检查日志
tail -50 logs/cshine.log

# 检查端口占用
lsof -i :8000

# 手动启动查看错误
cd /path/to/backend
source venv/bin/activate
python main.py
```

### 问题 3: OSS 上传失败
**症状**: 小程序上传文件失败
**解决**:
1. 检查 OSS 配置环境变量
2. 检查 OSS Bucket 权限
3. 检查小程序域名白名单
4. 查看后端日志中的 OSS 错误

### 问题 4: 知识库 API 返回 404
**症状**: 调用 /api/v1/folders 返回 404
**解决**:
```bash
# 检查路由是否注册
curl http://localhost:8000/docs | grep folders

# 检查代码是否正确部署
git log --oneline -5
git diff HEAD~1

# 重启服务
sudo systemctl restart cshine
```

---

## 📞 紧急联系

如果部署过程中遇到无法解决的问题：

1. **立即回滚**到上一个稳定版本
2. **保存现场**：
   ```bash
   # 导出错误日志
   tail -100 logs/cshine.log > error_$(date +%Y%m%d_%H%M%S).log
   
   # 记录系统状态
   systemctl status cshine > status_$(date +%Y%m%d_%H%M%S).txt
   ```
3. **联系技术支持**并提供错误日志

---

## 📚 相关文档

- [开发计划](./UPLOAD_FEATURE_PLAN.md)
- [实现总结](./UPLOAD_FEATURE_IMPLEMENTATION.md)
- [本地部署报告](./DEPLOYMENT_REPORT.md)
- [后端部署指南](./backend/deploy/README.md)

---

**文档版本**: v1.0  
**最后更新**: 2025-11-09  
**维护人**: DevOps Team

