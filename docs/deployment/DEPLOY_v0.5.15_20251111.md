# 线上部署方案 - v0.5.5 → v0.5.15

> **更新日期**: 2025-11-11  
> **更新类型**: 功能增强 + 重大修复  
> **优先级**: 🟡 建议（包含重要的功能修复）  
> **预计停机时间**: <5分钟

---

## 📋 更新摘要

从 v0.5.5 升级到 v0.5.15，主要包含：

### 🎉 重大功能
1. **通义听悟摘要功能完全修复**
   - 段落摘要、发言总结、思维导图全部正常工作
   - 修复数据解析和保存问题

2. **思维导图可视化**
   - 新增独立的思维导图组件
   - 多层级可视化展示

3. **会议重新处理功能**
   - 支持为旧会议重新生成摘要
   - 便于调试和修复

### 🔧 重要修复
- 上传功能优化（超时控制、错误处理）
- 参数处理优化（folder_id、title）
- 详情页返回按钮失效问题

---

## 🗄️ 数据库变更

### 新增表

#### 1. `contacts` 表（联系人管理）
```sql
CREATE TABLE contacts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    company VARCHAR(200),
    position VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contacts_user_id ON contacts(user_id);
CREATE INDEX idx_contacts_name ON contacts(name);
```

#### 2. `meeting_speakers` 表（说话人映射）
```sql
CREATE TABLE meeting_speakers (
    id SERIAL PRIMARY KEY,
    meeting_id UUID NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    speaker_id VARCHAR(50) NOT NULL,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE SET NULL,
    custom_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(meeting_id, speaker_id)
);

CREATE INDEX idx_meeting_speakers_meeting_id ON meeting_speakers(meeting_id);
CREATE INDEX idx_meeting_speakers_contact_id ON meeting_speakers(contact_id);
```

### 新增字段

#### `meetings` 表
```sql
ALTER TABLE meetings ADD COLUMN transcript_paragraphs TEXT;
```

**说明**：
- `transcript_paragraphs`: 存储通义听悟返回的段落化转录数据（JSON 格式）
- 包含说话人ID、时间戳、文本等详细信息

---

## 📦 依赖变更

### 无新增依赖

本次更新没有新增 Python 依赖，`requirements.txt` 保持不变。

---

## ⚙️ 环境变量变更

### 无新增环境变量

本次更新不需要修改 `.env` 文件。

---

## 🚀 部署步骤

### 方式 1：自动脚本（推荐）⭐

```bash
# 在服务器上执行
bash docs/deployment/UPDATE_SERVER.sh
```

脚本会自动：
1. ✅ 拉取最新代码
2. ✅ 激活虚拟环境
3. ✅ 执行数据库迁移
4. ✅ 重启后端服务
5. ✅ 验证服务状态

### 方式 2：手动步骤

#### 步骤 1：备份数据库

```bash
# SSH 登录服务器
ssh cshine@8.134.254.88

# 备份数据库
cd /home/cshine/Cshine
sudo -u postgres pg_dump cshine_db > backup_before_v0.5.15_$(date +%Y%m%d_%H%M%S).sql
```

#### 步骤 2：拉取代码

```bash
cd /home/cshine/Cshine
git fetch origin
git checkout main
git pull origin main
```

#### 步骤 3：执行数据库迁移

```bash
# 激活虚拟环境
source /home/cshine/Cshine/venv/bin/activate

# 执行迁移（PostgreSQL）
cd /home/cshine/Cshine/backend
python migrations/add_contacts_and_speakers.py
```

**预期输出**：
```
开始迁移...
✓ 创建 contacts 表
✓ 创建 meeting_speakers 表
✓ 添加 transcript_paragraphs 字段
迁移完成！
```

#### 步骤 4：重启后端服务

```bash
sudo systemctl restart cshine-api
```

#### 步骤 5：验证服务

```bash
# 检查服务状态
sudo systemctl status cshine-api

# 检查健康接口
curl http://localhost:8000/health

# 查看日志
sudo journalctl -u cshine-api -f --lines=50
```

---

## ✅ 验证方法

### 1. 健康检查

```bash
curl http://8.134.254.88:8000/health
```

**预期响应**：
```json
{"status":"healthy"}
```

### 2. 数据库验证

```bash
sudo -u postgres psql cshine_db -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('contacts', 'meeting_speakers');
"
```

**预期输出**：
```
     table_name      
--------------------
 contacts
 meeting_speakers
```

### 3. 字段验证

```bash
sudo -u postgres psql cshine_db -c "
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'meetings' 
AND column_name = 'transcript_paragraphs';
"
```

**预期输出**：
```
      column_name       | data_type 
-----------------------+-----------
 transcript_paragraphs | text
```

### 4. 功能测试

#### 测试 1：上传新音频
1. 在小程序中上传一个音频文件
2. 等待处理完成（约30-60秒）
3. 查看会议详情，确认有三个标签：总结、转录、思维导图
4. 检查数据是否完整

#### 测试 2：重新处理旧会议
1. 打开一个旧会议的详情页
2. 点击「🔄 重新处理」按钮
3. 确认重新处理
4. 等待完成后刷新，查看摘要数据

#### 测试 3：思维导图可视化
1. 打开有思维导图数据的会议
2. 切换到「思维导图」标签
3. 确认能看到层级化的节点展示
4. 检查时间戳和缩进是否正确

---

## 🔄 回滚方案

如果更新后出现问题，可以快速回滚：

### 步骤 1：回滚代码

```bash
cd /home/cshine/Cshine
git checkout v0.5.5  # 或具体的 commit hash
```

### 步骤 2：回滚数据库

```bash
# 删除新增的表和字段
sudo -u postgres psql cshine_db << EOF
DROP TABLE IF EXISTS meeting_speakers CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
ALTER TABLE meetings DROP COLUMN IF EXISTS transcript_paragraphs;
EOF
```

### 步骤 3：重启服务

```bash
sudo systemctl restart cshine-api
```

### 步骤 4：恢复备份（如果需要）

```bash
sudo -u postgres psql cshine_db < backup_before_v0.5.15_YYYYMMDD_HHMMSS.sql
```

---

## 📊 关键变更说明

### 1. 通义听悟摘要功能

**问题**：
- 之前摘要数据无法正确保存
- 数据格式解析错误

**修复**：
- 添加 `summarization_enabled = True` 标志
- 正确解析字典格式的数据
- 将列表/字典转换为 JSON 字符串保存

**影响**：
- 新上传的音频会自动生成完整摘要
- 旧会议可以通过「重新处理」生成摘要

### 2. 数据库结构变更

**新增表**：
- `contacts`: 管理常用联系人
- `meeting_speakers`: 映射说话人到联系人

**新增字段**：
- `meetings.transcript_paragraphs`: 段落化转录数据

**兼容性**：
- 所有字段都是可选的，不影响现有数据
- 旧会议仍然可以正常访问

### 3. 上传流程优化

**改进**：
- 合并上传和创建会议为单个原子操作
- 添加超时控制（60秒）
- 独立的上传模态框组件

**影响**：
- 上传更稳定，不会因页面刷新中断
- 更好的用户体验

---

## ⚠️ 注意事项

### 1. 数据迁移

- ✅ 迁移是**增量式**的，不会影响现有数据
- ✅ 新字段都是可选的，兼容旧数据
- ⚠️ 建议在低峰期执行迁移

### 2. 服务重启

- ⚠️ 重启期间会有短暂的服务中断（约10-30秒）
- ✅ 建议在用户较少的时间段执行
- ✅ 可以使用滚动更新减少影响

### 3. 通义听悟配置

- ✅ 确保通义听悟 AppKey 有效
- ✅ 确认账号已开通商用版
- ✅ 检查摘要功能是否已激活

### 4. 前端更新

- ⚠️ 小程序前端也需要同步更新
- ✅ 前端更新不需要审核（体验版即可测试）
- ✅ 建议先更新后端，再更新前端

---

## 📞 问题排查

### 问题 1：迁移失败

**症状**：执行迁移脚本时报错

**排查**：
```bash
# 检查数据库连接
sudo -u postgres psql cshine_db -c "SELECT version();"

# 检查表是否已存在
sudo -u postgres psql cshine_db -c "\dt"

# 查看详细错误
python migrations/add_contacts_and_speakers.py 2>&1 | tee migration.log
```

**解决**：
- 如果表已存在，跳过迁移
- 如果连接失败，检查数据库服务
- 如果权限不足，检查数据库用户权限

### 问题 2：服务启动失败

**症状**：重启后服务无法启动

**排查**：
```bash
# 查看服务状态
sudo systemctl status cshine-api

# 查看详细日志
sudo journalctl -u cshine-api -n 100 --no-pager

# 手动启动测试
cd /home/cshine/Cshine/backend
source /home/cshine/Cshine/venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**解决**：
- 检查 Python 依赖是否完整
- 检查数据库连接配置
- 检查端口是否被占用

### 问题 3：摘要功能不工作

**症状**：上传音频后没有生成摘要

**排查**：
```bash
# 查看后端日志
sudo journalctl -u cshine-api -f | grep -E "摘要|Summarization"

# 检查通义听悟配置
grep -E "TINGWU|ALIYUN" /home/cshine/Cshine/backend/.env

# 测试重新处理
curl -X POST http://localhost:8000/api/v1/meeting/{meeting_id}/reprocess \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**解决**：
- 检查通义听悟 AppKey 是否有效
- 确认账号是否开通了摘要功能
- 查看日志中的详细错误信息

---

## 📈 性能影响

### 数据库

- **新增表**: 2 个（contacts, meeting_speakers）
- **新增字段**: 1 个（transcript_paragraphs）
- **存储增长**: 约 1-2 KB/会议（取决于转录长度）
- **查询性能**: 已添加索引，影响可忽略

### 后端服务

- **内存使用**: 无明显增加
- **CPU使用**: 无明显增加
- **响应时间**: 无明显变化

### 通义听悟

- **处理时间**: 30-60秒/音频（取决于长度）
- **API调用**: 每个音频 1 次
- **成本**: 按通义听悟商用版计费

---

## 📝 更新日志

详见：`docs/core/CHANGELOG.md`

关键版本：
- v0.5.15: 修复返回按钮失效
- v0.5.14: 思维导图可视化
- v0.5.13: 通义听悟摘要完全修复
- v0.5.12: 会议重新处理功能
- v0.5.11: 摘要功能启用

---

## ✅ 部署检查清单

部署前：
- [ ] 已备份数据库
- [ ] 已通知相关人员
- [ ] 已选择合适的时间窗口
- [ ] 已准备回滚方案

部署中：
- [ ] 代码已拉取到最新
- [ ] 数据库迁移已执行
- [ ] 服务已重启
- [ ] 健康检查通过

部署后：
- [ ] 功能测试通过
- [ ] 日志无异常
- [ ] 性能正常
- [ ] 用户反馈良好

---

**部署负责人**: _________  
**部署时间**: _________  
**验证人**: _________  

---

**Let Your Ideas Shine. ✨**

