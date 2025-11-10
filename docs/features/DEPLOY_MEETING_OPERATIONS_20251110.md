# 🚀 会议操作功能完善 线上部署方案

> **更新类型**: 新功能 + Bug修复  
> **更新日期**: 2025-11-10  
> **是否必须**: 建议 🟡  
> **预计停机时间**: 无

---

## 📋 更新内容

### 1. 功能说明

本次更新全面完善了会议操作功能，新增会议重命名、复制、移动、删除功能，并优化了操作后的交互逻辑（自动跳转到目标知识库）。同时统一使用微信原生组件，提升用户体验。

**核心功能**：
- ✨ 会议重命名：长按会议卡片可重命名标题
- ✨ 会议复制：复制会议到指定知识库，标题自动添加"（副本）"
- ✨ 会议移动：移动会议到指定知识库（已优化）
- ✨ 会议删除：长按会议可直接删除
- 🎯 智能跳转：复制/移动后自动跳转到目标知识库

**技术优化**：
- 统一使用微信原生组件（ActionSheet、Modal）
- 知识库选择器支持无限滚动（突破 ActionSheet 6 项限制）
- 动态加载知识库列表
- 清理硬编码演示数据

### 2. 涉及文件

#### 后端文件
- `backend/app/api/meeting.py` - 新增 `copy_meeting` 端点，实现会议复制功能
- `backend/app/schemas.py` - `MeetingUpdate` 添加 `folder_id` 字段，支持更新会议所属知识库

#### 前端文件
- `pages/meeting/list.js` - 重构会议操作逻辑，新增 `switchToFolder`、`loadFolderList` 等方法
- `pages/meeting/list.wxml` - 优化 UI 组件，新增知识库选择器 Modal
- `pages/meeting/list.wxss` - 更新样式
- `utils/api.js` - 新增 `copyMeeting` API 方法
- `utils/config.js` - 优化本地开发配置

#### 资源文件
- `assets/icons/copy.png` - 复制图标
- `assets/icons/delete.png` - 删除图标
- `assets/icons/move.png` - 移动图标
- `assets/icons/rename.png` - 重命名图标

### 3. 数据库变更
- [x] 无数据库变更（`folder_id` 字段已在 v0.5.0 中添加）

### 4. 依赖变更
- [x] 无新增依赖

### 5. 环境变量变更
- [x] 无新增环境变量

---

## ⚠️ 更新前检查

- [x] 代码已提交到 main 分支（commit: 07655c8）
- [x] 本地测试通过
- [x] 数据库备份已完成（无需备份，无数据库变更）
- [x] 了解回滚步骤

---

## 🚀 部署步骤

### 方式 1：使用自动脚本（推荐）

```bash
# SSH 登录服务器
ssh root@your_server_ip

# 切换到项目目录
cd /root/Cshine

# 运行更新脚本
bash docs/deployment/UPDATE_SERVER.sh

# 查看服务状态
sudo systemctl status cshine-backend
```

**预计用时**: 2-3 分钟

---

### 方式 2：手动更新

```bash
# 1. SSH 登录服务器
ssh root@your_server_ip

# 2. 切换到项目目录
cd /root/Cshine

# 3. 拉取最新代码
git fetch origin
git checkout main
git pull origin main

# 4. 激活虚拟环境（如果需要）
cd backend
source venv/bin/activate

# 5. 重启后端服务
sudo systemctl restart cshine-backend

# 6. 检查服务状态
sudo systemctl status cshine-backend

# 7. 查看日志确认启动成功
tail -50 logs/cshine.log
```

**预计用时**: 3-5 分钟

---

## ✅ 更新后验证

### 1. 服务状态检查
```bash
# 检查后端服务
sudo systemctl status cshine-backend

# 检查健康接口
curl http://localhost:8000/health
```

**期望结果**：
- 服务状态：`active (running)`
- 健康接口返回：`{"status": "ok"}`

### 2. API 功能测试

#### 测试会议复制接口
```bash
# 获取 token（替换为实际用户的 token）
TOKEN="your_jwt_token"

# 获取一个会议 ID
MEETING_ID="your_meeting_id"

# 测试复制接口
curl -X POST "http://localhost:8000/api/v1/meeting/${MEETING_ID}/copy" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"folder_id": 1}'
```

**期望结果**：
- 返回 200 状态码
- 返回新创建的会议对象
- 标题包含"（副本）"

#### 测试会议移动接口
```bash
# 测试移动接口（更新 folder_id）
curl -X PUT "http://localhost:8000/api/v1/meeting/${MEETING_ID}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"folder_id": 2}'
```

**期望结果**：
- 返回 200 状态码
- 会议的 `folder_id` 已更新

### 3. 小程序功能测试

在小程序中测试以下功能：

- [ ] **重命名会议**
  1. 长按会议卡片
  2. 选择"重命名"
  3. 输入新标题
  4. 点击确定
  5. 验证：标题已更新，列表已刷新

- [ ] **复制会议**
  1. 长按会议卡片
  2. 选择"复制到"
  3. 选择目标知识库
  4. 点击确定
  5. 验证：自动跳转到目标知识库，出现"xxx（副本）"

- [ ] **移动会议**
  1. 长按会议卡片
  2. 选择"移动到"
  3. 选择目标知识库
  4. 点击确定
  5. 验证：自动跳转到目标知识库，会议已移动

- [ ] **删除会议**
  1. 长按会议卡片
  2. 选择"删除"
  3. 确认删除
  4. 验证：会议已从列表中移除

- [ ] **知识库选择器**
  1. 触发"复制到"或"移动到"
  2. 验证：显示所有知识库（支持滚动）
  3. 验证：显示当前位置
  4. 验证：选中状态有 ✓ 标识

### 4. 日志检查
```bash
# 查看最近日志
tail -50 /root/Cshine/backend/logs/cshine.log

# 实时监控日志
tail -f /root/Cshine/backend/logs/cshine.log
```

**关注点**：
- 无错误日志
- 复制/移动操作有正确的日志记录
- API 响应时间正常

---

## 🔙 回滚方案

如果更新后出现问题，可以快速回滚：

```bash
# 1. 停止服务
sudo systemctl stop cshine-backend

# 2. 恢复到上一个版本
cd /root/Cshine
git reset --hard 310449f  # v0.5.0 的 commit hash

# 3. 重启服务
sudo systemctl start cshine-backend

# 4. 验证服务状态
sudo systemctl status cshine-backend
curl http://localhost:8000/health
```

**回滚影响**：
- 会议复制功能不可用
- 会议重命名/移动/删除功能不可用
- 其他功能不受影响
- 无数据丢失风险（因为没有数据库变更）

---

## 📊 更新记录

| 步骤 | 状态 | 完成时间 | 备注 |
|------|------|---------|------|
| 备份数据库 | ✅ | - | 无需备份（无数据库变更） |
| 拉取代码 | ⏳ | - | git pull origin main |
| 更新依赖 | ✅ | - | 无需更新（无依赖变更） |
| 重启服务 | ⏳ | - | systemctl restart cshine-backend |
| 功能验证 | ⏳ | - | 测试复制/移动/重命名/删除 |

**更新负责人**: [待填写]  
**更新执行时间**: [待填写]  
**更新结果**: [待填写]

---

## 💡 注意事项

1. **无停机时间**：本次更新无需停机，服务重启时间 < 5 秒
2. **向后兼容**：新增接口不影响现有功能
3. **前端更新**：小程序需要重新编译并发布
4. **测试建议**：建议先在测试环境验证，再部署到生产环境

---

## 📝 相关文档

- [CHANGELOG.md](../core/CHANGELOG.md) - v0.5.5 更新日志
- [后端更新协议](../deployment/BACKEND_UPDATE_PROTOCOL.md)
- [开发规范](../core/DEVELOPMENT_GUIDE.md)

---

**版本**: v0.5.5  
**文档创建时间**: 2025-11-10  
**文档作者**: AI Assistant

---

**Let Your Ideas Shine. ✨**

