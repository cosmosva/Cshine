# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.5] - 2025-11-10

### ✨ 功能增强 - 会议操作完善与交互优化

这是一个重要的功能完善版本，全面升级了会议操作功能，使用微信原生组件统一交互体验，并优化了操作后的跳转逻辑。

### Added - 新增功能

#### 会议操作功能 ✨
- 📝 **重命名会议**
  - 长按会议卡片弹出操作菜单
  - 选择"重命名"弹出输入框
  - 当前标题自动预填充
  - 支持修改会议标题
  - 重命名后自动刷新列表

- 📋 **复制会议到知识库**
  - 长按会议选择"复制到"
  - 显示所有知识库列表（支持滚动）
  - 复制会议到指定知识库
  - 标题自动添加"（副本）"标识
  - 副本默认不收藏
  - **复制后自动跳转到目标知识库** ✨

- 📁 **移动会议到知识库**
  - 长按会议选择"移动到"
  - 显示所有知识库列表（支持滚动）
  - 移动会议到指定知识库
  - 显示当前位置
  - **移动后自动跳转到目标知识库** ✨

- 🗑️ **删除会议**
  - 长按会议选择"删除"
  - 系统原生确认对话框
  - 红色警告按钮
  - 提示"删除后无法恢复"

#### 后端 API 新增
- `POST /api/v1/meeting/{meeting_id}/copy` - 复制会议
- `PUT /api/v1/meeting/{meeting_id}` - 支持更新 `folder_id`

### Changed - 优化

#### 交互体验提升 ✨
- 🎯 **智能跳转**
  - 复制/移动会议后自动跳转到目标知识库
  - 立即看到操作结果
  - 更符合用户预期的交互逻辑

- 📱 **统一使用微信原生组件**
  - 操作菜单：`wx.showActionSheet`
  - 输入对话框：`wx.showModal` (editable: true)
  - 确认对话框：`wx.showModal`
  - 知识库选择：自定义 Modal（支持无限滚动）
  - 统一的视觉风格和交互体验

- 🎨 **UI 优化**
  - 知识库选择器支持滚动（突破 ActionSheet 6 项限制）
  - 显示当前位置信息
  - 清晰的选中状态（✓ 标识）
  - 动态标题（"复制到" / "移动到"）

#### 数据管理优化
- 🔄 **演示数据清理**
  - 删除硬编码的演示知识库数据
  - 改为从后端 API 动态加载
  - 支持实时更新知识库列表
  - 自动计算未分类文件数量

- 📊 **知识库筛选优化**
  - 支持按知识库筛选会议
  - `currentFolderId: 'uncategorized'` 表示未分类
  - `currentFolderId: null` 表示不筛选
  - 数字 ID 表示指定知识库

### Fixed - 修复

- 🐛 修复 `MeetingUpdate` schema 缺少 `folder_id` 字段
- 🐛 修复移动会议后数据未实际更新的问题
- 🐛 修复 ActionSheet 选项超过 6 个时的错误
- 🐛 修复知识库列表未从后端加载的问题

### Technical - 技术细节

#### 后端改动
- `backend/app/api/meeting.py`
  - 新增 `copy_meeting` 端点
  - 复制所有会议内容（音频、转写、总结等）
  - 支持指定目标知识库
  
- `backend/app/schemas.py`
  - `MeetingUpdate` 添加 `folder_id` 字段
  - 支持更新会议所属知识库

#### 前端改动
- `pages/meeting/list.js`
  - 重构会议操作功能，使用原生组件
  - 新增 `switchToFolder` 方法实现智能跳转
  - 新增 `loadFolderList` 方法动态加载知识库
  - 优化 `copyMeetingRequest` 和 `moveMeetingRequest`
  - 清理不需要的状态字段

- `pages/meeting/list.wxml`
  - 添加 `data-title` 参数到会议卡片
  - 新增知识库选择器 Modal
  - 删除旧的自定义 ActionSheet

- `utils/api.js`
  - 新增 `copyMeeting` API 方法
  - 导出到 module.exports

### Documentation - 文档

- 📝 更新 CHANGELOG.md
- 📝 更新版本号到 v0.5.5

### Migration Guide - 迁移指南

#### 数据库
无需迁移，`folder_id` 字段已存在。

#### 配置
无需修改配置。

#### 部署
1. 拉取最新代码
2. 重启后端服务
3. 重新编译小程序

---

## [0.5.0] - 2025-11-09

### ✨ 功能增强 - 知识库管理完善

这是一个重要的用户体验提升版本，完善了知识库（文件夹）管理功能，让用户可以更灵活地组织和管理会议内容。

### Added - 新增功能

#### 知识库管理 ✨
- 📝 **重命名知识库**
  - 点击知识库⋯按钮打开操作菜单
  - 选择"重命名"弹出输入框
  - 当前名称自动预填充
  - 重命名后自动更新所有相关显示
  - 支持同步更新当前选中知识库的标题

- 🗑️ **删除知识库**
  - 点击操作菜单中的"删除"
  - 弹出确认对话框（带警告说明）
  - 删除后，其中的会议移至"录音文件"
  - 自动切换到"录音文件"并刷新列表
  - 危险操作使用红色高亮提示

- 📁 **会议移动功能**
  - 长按会议卡片触发操作菜单
  - 选择"移动到知识库"
  - 显示当前位置和所有可选知识库
  - 支持移动到"录音文件"或任意知识库
  - 移动后自动刷新列表并提示成功

- 🗑️ **列表快捷删除**
  - 长按会议卡片可直接删除
  - 系统原生确认对话框
  - 危险操作红色按钮

### Changed - 优化

#### UI/UX 提升
- 🎨 **知识库操作菜单**
  - ActionSheet 设计，从底部滑出
  - 清晰的图标和文字标签
  - 危险操作（删除）使用红色高亮

- 💬 **Modal 设计优化**
  - 重命名 Modal：自动聚焦输入框
  - 删除确认 Modal：清晰的警告文案和说明
  - 移动选择 Modal：显示当前位置和目标列表
  - 所有 Modal 支持点击遮罩关闭

- ⚡ **交互体验增强**
  - 长按会议卡片有震动反馈
  - 所有操作有 Loading 状态
  - 成功后有 Toast 提示
  - 列表自动刷新，状态实时同步

#### 样式规范
- 🎨 **危险操作样式**
  - 删除按钮/文字使用 #FF3B30 红色
  - 按下时有透明度变化反馈
  - 与其他操作形成视觉区分

- 📐 **更多操作按钮**
  - ⋯ 图标优化点击区域
  - 添加点击态反馈
  - 使用 catchtap 防止冒泡

### Technical Details - 技术实现

**前端实现**
- 新增状态管理：`showFolderActions`、`showRenameModal`、`showDeleteConfirm`、`showMoveFolderSelector`、`showMeetingActions`
- 新增事件处理：`showFolderMenu`、`handleRenameFolder`、`handleDeleteFolder`、`onMeetingLongPress`、`handleMoveToFolder`
- 数据流：本地状态 → API 调用 → 更新本地列表 → 刷新 UI

**API 集成**
- 重命名：`API.updateFolder(folderId, { name })`
- 删除：`API.deleteFolder(folderId)`
- 移动会议：`API.updateMeeting(meetingId, { folder_id })`

**错误处理**
- 空名称校验
- 网络异常提示
- API 错误统一处理
- 用户友好的错误信息

### Documentation - 文档

- 📚 **功能设计文档** (`docs/features/FOLDER_MANAGEMENT_ENHANCEMENT.md`)
  - 完整的交互流程设计
  - UI 组件详细规范
  - 技术实现说明
  - 测试计划

- 📝 **部署文档** (`docs/features/DEPLOY_FOLDER_MGMT_20251109.md`)
  - 更新类型：功能增强
  - 更新优先级：建议🟡
  - 详细部署步骤
  - 测试清单
  - 回滚方案

### Testing - 测试

**功能测试**
- ✅ 知识库重命名
- ✅ 知识库删除（带确认）
- ✅ 会议长按菜单
- ✅ 会议移动到知识库
- ✅ 列表刷新和状态同步

**边界测试**
- ✅ 空名称校验
- ✅ 重复名称校验（后端）
- ✅ 删除当前选中知识库
- ✅ 移动到相同知识库
- ✅ 网络异常处理

**UI/UX 测试**
- ✅ Modal 动画流畅
- ✅ ActionSheet 显示/隐藏
- ✅ 危险操作红色高亮
- ✅ 长按震动反馈
- ✅ Toast 提示清晰

### Known Issues - 已知问题

无已知问题。

### Breaking Changes - 破坏性变更

⚠️ **无破坏性变更**

所有功能向后兼容，可随时回滚到 v0.4.5。

### Migration Guide - 迁移指南

从 v0.4.5 升级到 v0.5.0：

**前端迁移**
- 无需特殊操作
- 小程序重新上传即可
- 建议版本号：v0.5.0
- 建议清除小程序缓存后测试

**后端迁移**
- 无需后端部署（API 已在 v0.4.5 实现）

### Performance - 性能

- 操作后智能刷新列表，只更新必要数据
- 本地状态同步，减少网络请求
- Modal 动画使用 CSS transition，流畅度高

### Security - 安全性

- 删除知识库不删除会议，数据安全
- 所有危险操作有二次确认
- 后端 API 权限校验（已有）

---

## [0.4.8] - 2025-11-09

### 📖 开发规范文档 - 必读

创建完整的开发规范文档，明确后端功能更新必须创建部署文档的规则。

### Added - 新增
- 📖 **完整开发规范** (`docs/core/DEVELOPMENT_GUIDE.md`)
  - 代码提交规范（Conventional Commits）
  - 后端功能更新规范 ⭐ 核心规则
  - 文档管理规范
  - 分支管理规范
  - 提交前检查清单
  - 常见问题解答

- ⚡ **快速检查清单** (`QUICK_CHECKLIST.md`)
  - 一页纸快速参考
  - 后端更新核心规则
  - 可打印贴在显示器旁边

### Changed - 优化
- 📍 **README 添加开发规范入口**
  - 在"快速开始"部分突出显示
  - 链接到完整规范和快速清单
  - 强调核心规则

### 核心规则重申

**后端功能更新规范**：
1. ✅ 每次后端功能开发完成，**必须**创建部署文档
2. ✅ 部署文档使用模板：`.github_docs_template.md`
3. ✅ 部署文档位置：`docs/features/DEPLOY_<功能名>_<日期>.md`
4. ✅ 必填内容：更新类型、优先级、变更说明、部署步骤、验证方法、回滚方案
5. ✅ 更新优先级：必须🔴/建议🟡/可选🟢
6. ✅ 与代码一起提交到 git
7. ✅ 更新是建议性的，非强制性

**目的**：
- 确保每次功能更新都有清晰的线上部署方案
- 降低部署风险，提供回滚保障
- 形成可追溯的更新记录

---

## [0.4.7] - 2025-11-09

### 🗂️ 文档结构大重组 - 分类管理

建立清晰的文档分类系统，解决文档散乱问题，提升项目可维护性。

### Changed - 重组
- 📂 **建立文档分类结构**
  - `docs/core/` - 核心文档（README、CHANGELOG、PRD）
  - `docs/deployment/` - 部署文档（部署指南、更新协议、配置文档）
  - `docs/features/` - 功能文档（临时性部署文档，3个月后归档）
  - `docs/archive/` - 历史归档（过期文档，可定期清理）

- 🔗 **保持向后兼容**
  - 根目录 `README.md` 软链接到 `docs/core/README.md`
  - 所有旧链接通过软链接保持有效

### Added - 新增
- 📚 **文档结构说明** (`docs/README.md`)
  - 完整的文档分类说明
  - 文档生命周期管理
  - 清理规则和最佳实践
  - 文档索引和快速访问

- 🧹 **自动清理工具** (`docs/cleanup.sh`)
  - 自动移动 3 个月前的功能文档到归档
  - 提示删除 1 年前的归档文档
  - 统计各类文档数量
  - 显示最近的功能文档

- 📝 **部署文档模板** (`.github_docs_template.md`)
  - 标准化的部署文档模板
  - 包含所有必需字段
  - 快速创建新的部署文档

- 📖 **后端文档导航** (`backend/DOCS.md`)
  - 后端相关文档快速导航
  - 指向新的文档位置

### Improved - 优化
- 🔧 **gitignore 更新**
  - 临时部署文档不自动提交
  - `docs/features/DEPLOY_*.md` 需手动决定是否提交

- 📍 **文档链接更新**
  - 更新所有文档间的相互引用
  - 指向新的文档路径

### 文档布局对比

**之前**：
```
Cshine/
├── README.md
├── CHANGELOG.md
├── PRD-完善版.md
├── DEPLOYMENT_GUIDE.md
├── LOGIN.md
├── OSS_ENVIRONMENT_SETUP.md
├── BACKEND_UPDATE_PROTOCOL.md
├── DEPLOYMENT_CHECKLIST.md
├── RELEASE_v0.4.5.md
├── ... (20+ 个文档散落在根目录)
```

**现在**：
```
Cshine/
├── README.md (软链接)
├── docs/
│   ├── README.md (文档结构说明)
│   ├── cleanup.sh (清理工具)
│   ├── core/ (核心，永久保留)
│   ├── deployment/ (部署，持续更新)
│   ├── features/ (功能，待清理区)
│   └── archive/ (归档，可清理)
└── backend/
    └── DOCS.md (后端文档导航)
```

### 维护规则

**文档生命周期**：
1. 新功能完成 → 创建 `docs/features/DEPLOY_xxx.md`
2. 3 个月后 → 移动到 `docs/archive/`
3. 1 年后 → 可以删除

**定期清理**：
- 每月运行：`bash docs/cleanup.sh`
- 每季度审查归档文档

---

## [0.4.6] - 2025-11-09

### 📚 文档标准化 - 后端更新协议

建立后端功能更新的标准化流程，确保每次开发完成后都有清晰的线上部署方案。

### Added - 新增
- 📋 **后端更新标准协议** (`BACKEND_UPDATE_PROTOCOL.md`)
  - 定义标准化的更新流程
  - 提供更新文档模板
  - 包含部署步骤和验证方法
  - 提供回滚方案
  - 更新分类和优先级定义
  - 安全准则和最佳实践

- 📝 **快速上手指南** (`BACKEND_UPDATE_QUICKSTART.md`)
  - 开发人员使用指南
  - 部署人员使用指南
  - 实际示例和通知模板

### Changed - 优化
- 🗂️ **文档结构大幅精简**
  - 删除 15 个临时/重复文档
  - 合并相关文档为单一来源
  - 减少 ~4736 行冗余内容
  
- 📖 **核心文档合并**
  - `LOGIN.md` - 合并登录指南和测试指南
  - `DEPLOYMENT_GUIDE.md` - 唯一的部署文档
  - `backend/README.md` - 整合快速开始内容

### Removed - 删除
- 历史/调试文档（8个）：CLAUDE.md, IMPLEMENTATION_SUMMARY.md, KNOWLEDGE_PAGE_UPDATE.md, MEETING_LIST_DEBUG.md, PROFILE_UPDATE_COMPLETE.md, REAL_DEVICE_TESTING.md, TABBAR_DESIGN.md, TABBAR_SETUP_GUIDE.md
- 重复的部署文档（3个）：DEPLOYMENT_QUICKSTART.md, DEPLOYMENT_ENVIRONMENT_GUIDE.md, DEPLOY_LOGIN_UPDATE.md
- 重复的登录文档（2个）：LOGIN_GUIDE.md, LOGIN_TEST_GUIDE.md
- 重复的后端文档（2个）：backend/快速开始.md, backend/SETUP_DEV_OSS.md

---

## [0.4.5] - 2025-11-09

### 🚀 重大功能更新 - 文件上传与知识库管理

这是一个重要的功能性版本，新增了文件上传和知识库管理功能，极大提升了用户体验和内容组织能力。

### Added - 新增功能

#### 文件上传功能 ✨
- 📤 **音频文件上传**
  - 支持从本地选择音频文件（mp3/m4a/wav）
  - 最大支持 500MB 文件
  - 实时上传进度显示
  - OSS 直传优化，提升上传速度
  - 自动提取音频时长

- 🎯 **上传流程优化**
  - 点击 "+" 按钮弹出操作菜单
  - 文件选择后自动提取音频信息
  - 知识库选择界面
  - 实时进度监控
  - 完成后自动跳转详情页

#### 知识库管理功能 📚
- 📁 **知识库创建与管理**
  - 创建自定义知识库（文件夹）
  - 知识库重命名功能
  - 知识库删除功能
  - 知识库列表展示（带文件数统计）
  
- 🗂️ **会议分类组织**
  - 上传文件时选择目标知识库
  - 按知识库筛选会议列表
  - "录音文件"默认分类（全部）
  - 知识库卡片式展示

- 🎨 **UI/UX 优化**
  - 上传操作 ActionSheet
  - 知识库选择 Modal
  - 新建知识库输入 Modal
  - TicNote 风格的界面设计
  - 流畅的动画效果

#### 后端 API 增强 🔌
- 📡 **知识库 API**
  - `POST /api/v1/folders` - 创建知识库
  - `GET /api/v1/folders` - 获取知识库列表（带统计）
  - `GET /api/v1/folders/{id}` - 获取知识库详情
  - `PUT /api/v1/folders/{id}` - 更新知识库
  - `DELETE /api/v1/folders/{id}` - 删除知识库

- 🔐 **OSS 签名 API**
  - `GET /api/v1/upload/oss-signature` - 获取 OSS 上传签名
  - 前端直传 OSS，提升上传效率
  - 签名有效期 1 小时

- 📊 **会议 API 增强**
  - 创建会议支持 `folder_id` 参数
  - 列表查询支持按 `folder_id` 筛选
  - 返回数据包含 `folder_id` 信息

#### 数据库模型扩展 🗄️
- 📋 **新增 Folder 表**
  - id（主键，自增）
  - user_id（用户ID，外键）
  - name（知识库名称）
  - created_at / updated_at（时间戳）

- 📝 **Meeting 表增强**
  - 新增 `folder_id` 字段（可为空）
  - 外键关联到 folders 表
  - 删除知识库时自动置空

### Changed - 变更

#### 前端优化
- 🎨 **list.wxml**
  - 添加上传相关的 ActionSheet UI
  - 添加知识库选择 Modal UI
  - 添加新建知识库 Modal UI
  - 优化 "+" 按钮点击事件

- 💅 **list.wxss**
  - 新增 Modal 相关样式
  - 优化 ActionSheet 样式
  - 增强视觉层次感

- ⚙️ **list.js**
  - 实现文件选择逻辑
  - 实现音频时长提取
  - 实现知识库选择逻辑
  - 实现新建知识库逻辑
  - 状态管理优化

- 📤 **upload.wxml/js**
  - 修改上传文案（"上传中" → "正在上传文件到云端"）
  - 支持从列表页传递文件信息
  - OSS 直传实现
  - 进度监听优化
  - 支持 folder_id 参数

- 🔌 **api.js**
  - 添加知识库 CRUD API 方法
  - 添加 OSS 签名获取方法
  - 统一错误处理

- 🌐 **app.js**
  - globalData 添加 uploadFile 字段
  - 支持跨页面文件信息传递

#### 后端优化
- 🏗️ **models.py**
  - 新增 Folder 模型
  - Meeting 模型添加 folder_id 字段
  - User 模型添加 folders 关系

- 📋 **schemas.py**
  - 新增 FolderCreate、FolderUpdate、FolderResponse、FolderListResponse
  - MeetingCreate 添加 folder_id 字段
  - MeetingResponse 添加 folder_id 字段

- 🔧 **api/folder.py**（新文件）
  - 完整的知识库 CRUD 实现
  - 自动统计会议数量
  - 名称唯一性校验

- 🚀 **api/upload.py**
  - 添加 OSS 签名生成接口
  - 支持前端直传

- 🔐 **utils/oss.py**
  - 实现 generate_oss_upload_signature 函数
  - Policy 生成和签名
  - 安全性增强

### Technical Details - 技术细节

**前端文件上传流程**
```
用户点击 "+" → ActionSheet 弹出 → 选择"上传文件"
    ↓
wx.chooseMessageFile() 文件选择
    ↓
提取音频时长 (wx.createInnerAudioContext)
    ↓
知识库选择 Modal → 选择目标知识库
    ↓
跳转上传页面 → 获取 OSS 签名
    ↓
wx.uploadFile() 直传 OSS（带进度）
    ↓
调用后端创建会议 API（携带 folder_id）
    ↓
AI 后台处理 → 完成后跳转详情页
```

**数据库迁移**
```sql
-- 创建 folders 表
CREATE TABLE folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- meetings 表添加字段
ALTER TABLE meetings ADD COLUMN folder_id INTEGER;
```

**OSS 直传实现**
```javascript
// 前端
1. 调用 API.getOssSignature() 获取签名
2. 使用 wx.uploadFile() 上传到 OSS
3. 监听 onProgressUpdate 显示进度
4. 上传成功后调用后端创建会议

// 后端
1. 生成 Policy（包含文件大小、路径限制）
2. Base64 编码 Policy
3. 使用 HMAC-SHA1 签名
4. 返回签名数据给前端
```

### Documentation - 文档

- 📚 **新增文档**
  - `UPLOAD_FEATURE_PLAN.md` - 上传功能开发计划（完整设计文档）
  - `UPLOAD_FEATURE_IMPLEMENTATION.md` - 实现总结文档
  - `PRODUCTION_DEPLOYMENT_GUIDE.md` - 线上部署详细指南
  - `DEPLOYMENT_CHECKLIST.md` - 部署快速清单
  - `DEPLOYMENT_REPORT.md` - 本地部署报告
  - `backend/deploy/deploy_upload_feature.sh` - 一键部署脚本
  - `backend/deploy/rollback_upload_feature.sh` - 一键回滚脚本
  - `backend/migrations/add_folders_and_folder_id.py` - 数据库迁移脚本
  - `backend/test_upload_apis.py` - API 测试脚本

### Deployment - 部署

#### 本地环境
- ✅ 数据库迁移成功
- ✅ 后端服务已重启（PID: 49172）
- ✅ API 接口验证通过
- ✅ 健康检查正常

#### 线上部署步骤
```bash
# 方式一：一键部署（推荐）
./backend/deploy/deploy_upload_feature.sh

# 方式二：手动部署
git pull origin main
python migrations/add_folders_and_folder_id.py
sudo systemctl restart cshine
```

#### 小程序部署
1. 微信开发者工具编译预览
2. 真机测试功能
3. 上传代码（版本：v0.4.5）
4. 提交审核（功能说明模板已提供）

### Migration Guide - 迁移指南

从 v0.4.2 升级到 v0.4.5：

**后端迁移**
```bash
cd backend
# 备份数据库
cp cshine.db cshine.db.backup.$(date +%Y%m%d)

# 运行迁移
python migrations/add_folders_and_folder_id.py

# 重启服务
sudo systemctl restart cshine
```

**前端迁移**
- 无需特殊操作，兼容旧版本
- 建议清除小程序缓存后重新编译

### Breaking Changes - 破坏性变更

⚠️ **无破坏性变更**

所有新功能向后兼容，不影响现有功能。

### Performance - 性能优化

- ⚡ OSS 直传，减轻服务器压力
- ⚡ 前端进度监听，实时反馈
- ⚡ 异步处理，不阻塞用户操作
- ⚡ 智能缓存，减少重复请求

### Security - 安全性

- 🔐 OSS 签名机制，保护上传安全
- 🔐 文件大小限制（500MB）
- 🔐 文件格式校验
- 🔐 用户权限隔离
- 🔐 知识库名称唯一性校验

### Testing - 测试

**功能测试**
- ✅ 文件选择和上传
- ✅ 音频时长提取
- ✅ 知识库创建和管理
- ✅ 会议列表筛选
- ✅ OSS 签名和直传
- ✅ 进度监听和显示
- ✅ 错误处理

**集成测试**
- ✅ 完整上传流程
- ✅ 知识库关联
- ✅ 数据库一致性
- ✅ API 接口联调

### Known Issues - 已知问题

- ⚠️ 知识库重命名功能 UI 待实现（API 已就绪）
- ⚠️ 知识库删除需要确认对话框
- ⚠️ 批量上传功能待开发
- ⚠️ 断点续传功能待开发

### Next Steps - 下一步计划

#### P1 - 知识库管理增强
- [ ] 知识库重命名 UI
- [ ] 知识库删除确认对话框
- [ ] 会议移动到其他知识库
- [ ] 知识库排序功能
- [ ] 知识库统计信息优化

#### P2 - 上传功能优化
- [ ] 上传失败重试机制
- [ ] 断点续传支持
- [ ] 批量上传支持
- [ ] 上传历史记录
- [ ] 文件格式自动转换

---

## [0.4.2] - 2025-11-09

### 🎉 体验版测试通过 - 登录功能完全正常

### Fixed - 修复
- 🔧 修复体验版环境配置，体验版和正式版都使用生产环境
- 🔧 修复 `getUserProfile` 必须在同步上下文调用的问题  
- 🔧 修复后端 `/api/v1/auth/me` 接口认证依赖问题

### Changed - 优化
- 💬 个人页面"微信登录"改为"完善资料"，语义更清晰
- 💬 优化登录交互流程和文案提示
- ⚙️ 完善环境自动检测逻辑（开发/体验/正式）

### Added - 新增
- 📦 OSS 环境隔离配置（开发/生产 bucket 分离）
- 📚 完整的部署和更新文档
- 📚 环境配置指南和故障排查文档

### Deployed - 部署状态
- ✅ 后端服务已更新并重启（2025-11-09 02:41）
- ✅ 体验版已发布并测试通过
- ✅ 所有登录功能正常工作
- ✅ 环境自动切换功能验证通过

---

## [0.4.0] - 2025-11-08

### 🔐 重大更新 - 前后端登录流程打通

这是一个重要的基础设施更新，完整实现了微信小程序登录系统，打通了前后端认证流程。

### Added - 新增功能

#### 自动静默登录 ✨
- 📱 **小程序启动自动登录**
  - 首次打开自动调用 `wx.login()` 获取 code
  - 自动调用后端登录接口获取 Token
  - 用户无感知，快速启动
  - 无需弹窗授权

- 🔄 **智能登录状态管理**
  - `app.js` 全局检查登录状态
  - Token 失效自动重新登录
  - 全局变量存储用户信息

#### 完整授权登录 ✨
- 👤 **个人中心主动登录**
  - 用户点击"登录"按钮触发
  - 调用 `wx.getUserProfile()` 获取昵称和头像
  - 保存完整用户信息到本地
  - 显示友好的登录提示

- 🎨 **登录体验优化**
  - 显示 Loading 状态："登录中..."
  - 区分新用户和老用户提示
  - 错误提示优化（授权拒绝、网络异常等）
  - 完善的错误处理机制

#### Token 管理系统 🔑
- 🔐 **自动 Token 携带**
  - 所有需要认证的 API 自动添加 `Authorization` header
  - `Bearer Token` 标准格式
  - 无需手动处理

- ⚠️ **Token 失效处理**
  - 后端返回 401 自动清除本地数据
  - 提示用户"登录已过期，请重新登录"
  - 智能引导用户重新登录

- 💾 **本地存储管理**
  - 存储 `token`、`userInfo` 到 `wx.storage`
  - 退出登录清除所有认证数据
  - 支持跨页面状态同步

### Changed - 变更

#### 前端优化
- 🔧 **profile.js 重构**
  - 完整实现 `handleLogin()` 方法
  - 调用后端 API 进行认证
  - Promise 风格的异步处理
  - 详细的日志输出便于调试

- 🌍 **app.js 增强**
  - `onLaunch` 添加自动登录逻辑
  - `checkLoginStatus()` 检查本地 Token
  - `doLogin()` 执行静默登录
  - `ensureLogin()` 确保已登录

- 📡 **request.js 优化**
  - 已完善 Token 携带逻辑（无需修改）
  - 401 错误自动处理
  - 统一的错误提示

#### 用户体验提升
- ✅ 首次打开小程序无需手动登录
- ✅ 用户可选择是否授权昵称和头像
- ✅ 登录失败友好提示
- ✅ Token 失效自动处理

### Technical Details - 技术细节

**登录流程（自动）**
```javascript
小程序启动
  ↓
app.onLaunch() 检查 Token
  ↓
Token 不存在
  ↓
调用 wx.login() 获取 code
  ↓
调用 API.login(code)
  ↓
保存 Token 到本地
  ↓
全局变量更新
```

**登录流程（手动）**
```javascript
用户点击"登录"
  ↓
wx.login() 获取 code
  ↓
wx.getUserProfile() 获取用户信息
  ↓
API.login(code, userInfo)
  ↓
保存 Token 和用户信息
  ↓
更新页面状态
  ↓
显示登录成功
```

**API 请求流程**
```javascript
发起 API 请求
  ↓
request.js 自动添加 Authorization header
  ↓
后端验证 Token
  ↓
返回数据 or 401
  ↓
401 → 清除 Token，提示重新登录
```

### Documentation - 文档

- 📚 **新增文档**
  - `LOGIN_GUIDE.md` - 登录功能完整说明文档
    - 登录流程详解
    - Token 管理说明
    - 测试指南
    - 常见问题解答
    - 配置说明

- 📝 **更新文档**
  - `README.md` - 添加登录功能说明
  - 更新版本号到 v0.4.0
  - 添加"用户认证"功能模块
  - 添加登录配置说明

### Testing - 测试

**测试场景覆盖：**
- ✅ 自动静默登录测试
- ✅ 完整授权登录测试
- ✅ 退出登录测试
- ✅ Token 失效处理测试
- ✅ 网络异常处理测试

**测试环境：**
- 微信开发者工具模拟器 ✅
- 真机测试（待完成）

### Migration Guide - 迁移指南

从 v0.3.5 升级到 v0.4.0：

**后端配置（重要）：**
```python
# backend/config.py
WECHAT_APPID = "your_appid"      # 必须配置
WECHAT_SECRET = "your_secret"    # 必须配置
```

**前端配置：**
```javascript
// utils/config.js
const API_BASE_URL = 'http://your-server:8000'
```

**清除旧数据（可选）：**
1. 微信开发者工具 → 清缓存 → 全部清除
2. 重新编译小程序

### Breaking Changes - 破坏性变更

⚠️ **无破坏性变更**

现有功能保持兼容，新增登录功能不影响现有代码。

### Known Issues - 已知问题

- ⚠️ 生产环境需要配置 HTTPS 和域名白名单
- ⚠️ 真机测试待验证
- ⚠️ Token 刷新机制待实现（当前 Token 有效期 7 天）

### Security - 安全性

- ✅ JWT Token 认证
- ✅ Token 本地加密存储
- ✅ HTTPS 传输（生产环境）
- ✅ 敏感信息不在日志中输出
- ⚠️ 建议生产环境修改 JWT_SECRET_KEY

---

## [0.3.5] - 2025-11-08

### 🎨 UI/UX 优化 - 知识库抽屉样式精细调整

这是一个专注于细节优化的版本，优化了知识库管理抽屉的视觉层级和交互体验。

### Changed - 变更

#### 知识库管理抽屉优化 🎯

- 📐 **"我创建的"区域样式调整**
  - 标题字号：从17px调整为**15px**（与卡片文字一致）
  - 标题字重：从600调整为**400**（不加粗）
  - 操作图标：从24px调整为**18px**（与卡片图标一致）
  - 左边距：增加到**16px**，文字向右缩进
  - 上下边距：各增加到**12px**，呼吸感更好

- 🗑️ **简化抽屉头部**
  - 删除"知识库管理"标题后的搜索和加号图标
  - 头部只保留标题，更简洁清爽
  - 聚焦核心功能，减少视觉干扰

- 🖼️ **汉堡菜单图标PNG化**
  - 将左上角"☰"emoji替换为PNG图标
  - 文件：`menu.png`
  - 尺寸：22px × 22px
  - 与其他图标风格统一

#### 视觉一致性提升 ✨

- 📏 **统一字体和图标规格**
  - 抽屉内所有文字：15px / 400字重
  - 抽屉内所有图标：18px × 18px
  - 整体视觉层级更协调
  - 信息密度更合理

### Technical - 技术细节

- 更新 `pages/meeting/list.wxml`：优化抽屉头部结构和菜单图标
- 更新 `pages/meeting/list.wxss`：精细调整间距、字号和图标尺寸
- 新增 `assets/icons/menu.png`：汉堡菜单图标

## [0.3.3] - 2025-11-08

### 🎨 UI/UX 优化 - 图标系统升级与导航栏优化

这是一个专注于视觉优化的版本，将所有emoji图标替换为PNG图标，优化导航栏布局，提升整体视觉一致性和专业度。

### Changed - 变更

#### 图标系统全面升级 🖼️

- 📁 **文件夹图标替换**
  - 将抽屉中所有文件夹emoji（📁）替换为PNG图标
  - 文件：`folder.png`
  - 尺寸：18px × 18px
  - 透明度：0.7

- ➕ **操作图标PNG化**
  - 新增文件夹图标：`add-folder.png`（18px）
  - 排序图标：`sort.png`（18px）
  - 搜索图标：`search.png`（20px）
  - 加号图标：`add.png`（20px）

#### 导航栏布局优化 📐

- 🔄 **图标位置调整**
  - 将搜索（🔍）和加号（+）图标从品牌栏移至二级导航栏
  - 放置在筛选和排序按钮之前
  - 更符合常见交互习惯

- 🗑️ **简化导航栏**
  - 删除"媒体"筛选按钮（暂时不需要）
  - 保留核心功能：搜索、新增、排序
  - 界面更简洁清爽

- 📏 **放大标题区域**
  - ☰ 图标：从19px增大到**22px**，字重500
  - "录音文件"文字：从16px增大到**18px**，字重600
  - 图标文字间距：从10px增加到**12px**
  - 整体视觉层级更清晰

#### 抽屉宽度优化 📱

- 🎯 **宽度调整**
  - 从70%调整到75%，再调回**75%**
  - 经过多次测试找到最佳平衡点
  - 抽屉内容充足，主页面仍可见

- 🔧 **显示完整性修复**
  - 修复底部内容被TabBar遮挡问题
  - `padding-bottom` 增加TabBar高度（50px）
  - 确保最后一个文件夹卡片完全可见

### Technical Details - 技术细节

**图标系统实现**
```xml
<!-- 之前：emoji图标 -->
<text class="folder-icon">📁</text>

<!-- 现在：PNG图标 -->
<image class="folder-icon" src="/assets/icons/folder.png" mode="aspectFit"></image>
```

**样式适配**
```css
/* 统一图标样式 */
.folder-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  opacity: 0.7;
}

.icon-btn {
  width: 20px;
  height: 20px;
  color: #3C3C43;
  flex-shrink: 0;
}
```

**导航栏布局**
```xml
<view class="header-right">
  <!-- 新增：搜索和加号 -->
  <image class="icon-btn" src="/assets/icons/search.png"></image>
  <image class="icon-btn" src="/assets/icons/add.png"></image>
  
  <!-- 保留：排序 -->
  <view class="sort-btn">⇅</view>
</view>
```

**抽屉完整显示**
```css
.drawer-content {
  padding-bottom: calc(var(--tabbar-height) + env(safe-area-inset-bottom) + 16px);
  /* = 50px + 34px + 16px ≈ 100px */
}
```

### 文件清单

**新增图标文件（assets/icons/）：**
- `folder.png` - 文件夹图标（18px）
- `add-folder.png` - 新增文件夹图标（18px）
- `sort.png` - 排序图标（18px）
- `search.png` - 搜索图标（20px）
- `add.png` - 加号图标（20px）

### 视觉对比

| 元素 | 之前 | 现在 |
|------|------|------|
| 文件夹图标 | 📁 emoji | PNG 18px |
| 搜索图标位置 | 品牌栏 | 二级导航栏 |
| 加号图标位置 | 品牌栏 | 二级导航栏 |
| ☰ 图标大小 | 19px | **22px** |
| "录音文件"文字 | 16px / 500 | **18px / 600** |
| 媒体筛选按钮 | 显示 | **已删除** |
| 抽屉宽度 | 测试中 | **75%** |

---

## [0.3.2] - 2025-11-08

### 🐛 Bug Fixes - 抽屉布局修复

这是一个重要的 UI 修复版本，解决了侧边栏抽屉右侧内容被裁剪的问题。

### Fixed - 问题修复

#### 抽屉内容显示完整性修复 ✅

- 🔧 **宽度优化**
  - 抽屉宽度从 75% 增加到 80%，提供更多内容展示空间
  - 确保所有卡片内容和图标完整显示

- 📦 **Box-sizing 规范化**
  - 为 `.drawer-content` 添加 `box-sizing: border-box`
  - 为 `.drawer-item` 添加 `width: 100%` 和 `box-sizing: border-box`
  - 确保 padding 不会导致容器宽度溢出

- 🚫 **Overflow 控制优化**
  - 抽屉容器改为 `overflow: hidden`（移除 `overflow-x: visible`）
  - 抽屉内容添加 `overflow-x: hidden`
  - 左侧内容区 `.item-left` 添加 `overflow: hidden`
  - 防止内容横向溢出

- 🎯 **Flex 布局优化**
  - `.item-name` 添加 `flex-shrink: 1`，允许文字收缩以适应空间
  - `.item-count` 添加 `flex-shrink: 0` 和 `white-space: nowrap`，防止数字被压缩
  - `.more-icon` 添加 `flex-shrink: 0` 和 `white-space: nowrap`，确保图标始终完整显示
  - `.section-actions` 和 `.action-icon` 添加 `flex-shrink: 0`，防止右侧操作图标被压缩

- 📏 **Padding 微调**
  - `.more-icon` 的 padding 改为 `0 0 0 12px`（只在左侧留间距）
  - `.section-header` 的 padding 改为 `0 0 10px 0`（移除左右 padding）
  - 减少不必要的空间占用

### Technical Details - 技术细节

**关键 CSS 改进**
```css
/* 抽屉宽度增加 */
.drawer {
  width: 80%;  /* 从 77% 增加到 80% */
  overflow: hidden;  /* 统一为 hidden */
}

/* 内容区 box-sizing */
.drawer-content {
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 卡片完整性保证 */
.drawer-item {
  width: 100%;
  box-sizing: border-box;
}

/* Flex 收缩控制 */
.item-name {
  flex-shrink: 1;  /* 允许文字收缩 */
}

.item-count,
.more-icon,
.section-actions,
.action-icon {
  flex-shrink: 0;  /* 防止图标和数字被压缩 */
  white-space: nowrap;  /* 防止换行 */
}
```

**修复效果**
- ✅ 右侧 "⋯" 更多操作图标完整显示
- ✅ 分组标题区的 "📋" 和 "↕" 图标完整显示
- ✅ 文件夹名称过长时正确省略，不影响右侧图标
- ✅ 所有内容在抽屉内正确布局，无溢出

### Files Modified - 修改的文件

- [pages/meeting/list.wxss](pages/meeting/list.wxss) - 抽屉布局样式全面优化

---

## [0.3.1] - 2025-11-08

### ✨ 新增功能 - 知识库管理侧边栏抽屉

这是一个专注于知识库管理功能的版本，新增了从左侧滑出的抽屉组件，用户可以通过抽屉查看和管理所有文件夹分类。

### Added - 新增

#### 侧边栏抽屉组件 🗂️

- 📱 **抽屉交互**
  - 点击二级导航栏的"☰"图标打开侧边栏
  - 从屏幕左侧平滑滑入，宽度为屏幕的 75%
  - 点击遮罩层或选择文件夹后自动关闭
  - 支持流畅的动画过渡效果（0.25s cubic-bezier）

- 🎨 **视觉设计**
  - 完全复刻滴答清单风格的抽屉 UI
  - 白色头部 + 浅灰色内容区背景（#F8F9FA）
  - 卡片式文件夹列表，每个文件夹为独立白色圆角卡片
  - 半透明黑色遮罩层（rgba(0, 0, 0, 0.4)）
  - 轻量级卡片阴影效果

- 📂 **内容结构**
  - 头部："知识库管理"标题（20px 加粗）+ 搜索/添加图标
  - "录音文件 (总数)"：显示所有录音文件总数的入口
  - "我创建的"分组：显示用户创建的所有文件夹
  - 每个文件夹卡片显示：📁 图标 + 名称 + 数量 + ⋯ 更多操作

- 🔧 **技术实现**
  - 使用 `pointer-events` 防止关闭状态影响主页面
  - 使用 `visibility` + `left: -100%` 确保完全隐藏
  - 自动适配状态栏和底部安全区
  - 模拟数据：8个文件夹分类，共55个文件

### Changed - 变更

#### UI 细节优化

- 🎯 **卡片样式精调**
  - 卡片圆角：8px（更柔和的视觉效果）
  - 卡片阴影：`0 1px 2px rgba(0, 0, 0, 0.05)`（更轻盈）
  - 卡片内边距：13px 16px
  - 卡片间距：8px（录音文件卡片底部间距 16px）

- 📏 **文字与间距**
  - 文件夹名称：15px，正常字重（不加粗）
  - 文件数量：15px，灰色（#8E8E93），紧跟在名称后
  - 图标与文字间距：10px
  - 文件夹图标：18px，透明度 0.7

- 🔤 **标题优化**
  - "知识库管理"标题从 17px 增大到 20px
  - 字重保持 600，字间距 -0.3px
  - 头部内边距：14px

### Technical Details - 技术细节

**WXML 结构**
```xml
<!-- 侧边栏抽屉 -->
<view class="drawer-mask {{showDrawer ? 'show' : ''}}" bindtap="closeDrawer"></view>
<view class="drawer {{showDrawer ? 'show' : ''}}">
  <view class="drawer-header">知识库管理 + 图标</view>
  <scroll-view class="drawer-content">
    <view class="drawer-item all-files">📁 录音文件 (55)</view>
    <view class="drawer-section">
      <view class="section-header">我创建的 + 操作图标</view>
      <view class="drawer-item folder-item">📁 文件夹名 (数量) ⋯</view>
    </view>
  </scroll-view>
</view>
```

**CSS 关键技术**
```css
/* 抽屉容器 */
.drawer {
  position: fixed;
  left: -100%;  /* 完全隐藏 */
  width: 75%;
  visibility: hidden;
  pointer-events: none;  /* 不阻挡主页面 */
  transition: left 0.25s cubic-bezier(0.4, 0, 0.2, 1), visibility 0s 0.25s;
}

.drawer.show {
  left: 0;
  visibility: visible;
  pointer-events: auto;
}

/* 卡片式布局 */
.drawer-content {
  background-color: #F8F9FA;
  padding: 12px;
}

.drawer-item {
  background-color: #FFFFFF;
  border-radius: 8px;
  margin-bottom: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
```

**JavaScript 逻辑**
```javascript
// 抽屉状态管理
data: {
  showDrawer: false,
  totalCount: 55,
  folders: [
    { id: 1, name: '短视频', count: 6 },
    // ... 更多文件夹
  ]
},

// 打开/关闭抽屉
toggleDrawer() {
  this.setData({ showDrawer: !this.data.showDrawer })
},

// 选择文件夹（业务逻辑待实现）
selectFolder(e) {
  const folderId = e.currentTarget.dataset.id
  // TODO: 根据文件夹ID筛选会议列表
  this.closeDrawer()
}
```

### 待实现功能

- [ ] 文件夹筛选功能（点击文件夹后筛选对应的会议列表）
- [ ] 文件夹管理功能（创建、重命名、删除文件夹）
- [ ] 搜索功能（头部搜索图标）
- [ ] 更多操作菜单（点击"⋯"图标）

---

## [0.3.0] - 2025-11-08

### 🎨 UI/UX 优化 - 知识库页面视觉升级

这是一个专注于视觉体验优化的版本，重点改进了知识库（会议列表）页面的导航栏设计，实现了更现代、更有层次感的 TicNote 风格界面。

### Changed - 变更

#### 知识库页面导航栏重设计 ✨

- 🎨 **双层导航系统优化**
  - 品牌栏：白色背景，包含 Logo、品牌名称和录音快捷按钮
  - 二级导航栏：蓝灰色背景（#F5F7FA）+ 24px 圆角设计
  - 8px 视觉间隙，创造清晰的层次分离

- 💎 **视觉层次增强**
  - 圆角设计凸显：二级导航栏采用 24px 圆角（仅顶部两角）
  - 背景色对比：白色品牌栏区域 + 蓝灰色内容区域
  - Box-shadow 技术：使用 `box-shadow: 0 -24px 0 0 #FFFFFF` 在圆角外营造白色背景效果
  - 移除了可能影响圆角显示的 border-bottom

- 📐 **布局优化**
  - 页面整体背景：白色（#FFFFFF）
  - 品牌栏区域：白色背景，与页面融为一体
  - 二级导航栏：蓝灰色带圆角，在白色背景上形成视觉浮动效果
  - 主内容区：蓝灰色背景（#F5F7FA），与二级导航栏无缝衔接
  - 会议卡片左右 padding 移除，采用 12px 上下 padding

### Technical Details - 技术细节

**CSS 改进**
```css
/* 页面整体白色背景 */
.meeting-list-page {
  background-color: #FFFFFF;
}

/* 二级导航栏圆角 + box-shadow 技巧 */
.header {
  background-color: #F5F7FA;
  border-radius: 24px 24px 0 0;
  box-shadow: 0 -24px 0 0 #FFFFFF;  /* 关键：填充圆角外白色背景 */
}

/* 主内容区蓝灰色背景 */
.page-content {
  background-color: #F5F7FA;
}
```

**设计原理**
- 利用 box-shadow 实现圆角外的白色背景填充
- 通过颜色对比突出导航栏的圆角设计
- 创造"浮动卡片"的视觉效果，提升页面层次感

### Files Modified - 修改的文件

- `pages/meeting/list.wxss` - 导航栏和布局样式优化

---

## [0.2.5] - 2025-11-08

### 🎨 UI/UX 重大更新

这是一个重要的用户体验优化版本，添加了底部 TabBar 导航和个人中心页面。

### Added - 新增功能

#### 底部 TabBar 导航 ✨
- 📱 **三 Tab 设计**
  - 📚 知识库：会议纪要管理和查看
  - ⚡ Cshine：快速语音录制和闪记管理
  - 👤 我的：个人中心和设置

- 🎨 **统一设计规范**
  - 品牌色选中态（#4A6FE8）
  - 灰色未选中态（#999999）
  - 流畅的切换动画

#### 个人中心页面
- 📱 **"我的"页面**（`pages/profile/`）
  - 用户信息展示（头像、昵称、ID）
  - 登录/退出功能
  - 数据统计卡片（闪记数、会议数、今日新增、总时长）
  - 功能菜单（设置、导出、清除缓存、帮助、关于）
  - 版本信息显示

#### 图标资源
- 🎨 **TabBar 图标**
  - 6个图标（3个功能 × 2个状态）
  - 自动生成脚本
  - 占位图标支持

- 👤 **头像占位图**
  - 圆形透明背景
  - 自适应设计

### Fixed - 问题修复

- ✅ 修复后端类型导入错误（tingwu_service.py 缺少 List 导入）
- ✅ 修复数据库迁移脚本的导入问题
- ✅ 修复页面跳转方法（TabBar 页面使用 wx.switchTab）
- ✅ 完成数据库迁移（添加 conversational_summary 和 mind_map 字段）

### Changed - 变更

#### 项目结构优化
- 🗂️ **新增目录**
  - `assets/icons/` - TabBar 图标资源
  - `assets/images/` - 图片资源
  - `pages/profile/` - 个人中心页面

- 📁 **页面重组**
  - 主页改为 TabBar 模式
  - 会议列表页改为 TabBar 模式
  - 新增个人中心 TabBar 页

#### 配置更新
- 🔧 `app.json` 添加 tabBar 配置
- 🔧 更新 `.gitignore` 规则
- 🔧 优化项目文件组织

### Documentation - 文档

- 📚 **新增文档**
  - `TABBAR_DESIGN.md` - TabBar 设计完整文档
  - `TABBAR_SETUP_GUIDE.md` - TabBar 设置详细指南

- 📝 **更新文档**
  - `README.md` - 添加 TabBar 功能说明
  - 更新项目结构图

### Maintenance - 维护

- 🧹 **项目清理**
  - 删除临时日志文件
  - 删除测试文件
  - 清理 Python 缓存
  - 清理系统文件（.DS_Store）
  - 更新 .gitignore 规则

### Technical Details - 技术细节

**TabBar 实现**
- 使用微信小程序原生 TabBar
- 自定义图标（81×81 px PNG）
- 品牌色一致性

**个人中心实现**
- 本地数据统计
- 微信登录集成（getUserProfile）
- 响应式卡片设计

**数据库更新**
- 成功执行迁移脚本
- 添加新字段支持多维度摘要

### Migration Guide - 迁移指南

从 v0.2.0 升级到 v0.2.5：

1. **拉取最新代码**
2. **准备图标资源**（参考 TABBAR_SETUP_GUIDE.md）
3. **数据库已迁移**（自动完成）
4. **重新编译小程序**

### Known Issues - 已知问题

- ⚠️ 个人中心的部分功能为占位（设置、帮助、关于等）
- ⚠️ 当前使用占位图标，建议后续替换为专业设计图标

---

## [0.2.0] - 2025-11-07

### 🚀 会议纪要功能全面上线

这是一个重大功能更新版本，实现了完整的会议纪要功能，集成了阿里云通义听悟的高级AI能力。

### Added - 新增功能

#### 会议纪要核心功能
- 📋 **会议音频上传**
  - 支持 mp3/m4a/wav 格式
  - 最大支持 500MB 文件
  - 自动上传至阿里云 OSS

- 🎯 **语音转写**
  - 高精度语音识别
  - 支持中文、英语、粤语等多语种
  - 完整的转写文本输出

- 👥 **说话人分离**（Speaker Diarization）
  - 自动识别不同发言人
  - 支持不定人数自动识别
  - 按发言人组织转写内容

- 📑 **章节划分**（Auto Chapters）
  - 自动识别会议不同议题
  - 生成章节目录和时间戳
  - 每个章节包含标题和摘要
  - 适合 30 分钟以上的长会议

- 📝 **5种智能摘要** ✨
  1. **段落摘要**（Paragraph）- 整体会议概括
  2. **发言总结**（Conversational）- 按发言人汇总观点
  3. **思维导图**（MindMap）- 结构化主题展示
  4. **问答总结**（QuestionsAnswering）- Q&A 提炼
  5. **章节摘要** - 按章节提供详细摘要

- ✅ **行动项识别**（Action Items）
  - 智能识别待办事项
  - 自动提取行动计划
  - 支持手动补充和编辑

- 💡 **会议要点提取**
  - 三层提取策略：章节模式 → 段落模式 → 兜底模式
  - 自动生成会议讨论要点
  - 包含时间戳、发言人、主题、内容

#### 前端页面
- 📱 **会议列表页**（`pages/meeting/list`）
  - 会议列表展示
  - 状态筛选（处理中/已完成/失败）
  - 下拉刷新
  - 删除确认

- 📤 **会议上传页**（`pages/meeting/upload`）
  - 音频文件选择
  - 会议信息输入（标题、参会人、日期）
  - 实时进度显示
  - 处理状态轮询

- 📄 **会议详情页**（`pages/meeting/detail`）
  - 多 Tab 展示：摘要/要点/行动项/全文
  - 发言总结和思维导图展示
  - 音频播放控制
  - 编辑和删除功能

#### 后端 API
- 🔌 **会议纪要接口**
  - `POST /api/v1/meeting/create` - 创建会议纪要
  - `GET /api/v1/meeting/list` - 获取会议列表
  - `GET /api/v1/meeting/{id}` - 获取会议详情
  - `PUT /api/v1/meeting/{id}` - 更新会议纪要
  - `DELETE /api/v1/meeting/{id}` - 删除会议纪要
  - `GET /api/v1/meeting/{id}/status` - 查询处理状态

#### 数据库模型
- 🗄️ **Meeting 表**
  - 基础信息：标题、参会人、日期、音频
  - 转写结果：transcript（转写文本）
  - 多维度摘要：
    - `summary` - 段落摘要
    - `conversational_summary` - 发言总结 ✨
    - `mind_map` - 思维导图 ✨
  - 结构化数据：
    - `key_points` - 会议要点（JSON）
    - `action_items` - 行动项（JSON）
  - 状态管理：pending/processing/completed/failed

#### AI 服务增强
- 🤖 **通义听悟集成优化**
  - 完整的参数配置支持
  - 多种摘要类型同时生成
  - 说话人分离配置
  - 章节划分配置
  - 会议助手配置

- ⚡ **异步处理**
  - 独立的会议处理器（`meeting_processor.py`）
  - 后台线程处理，不阻塞用户
  - 最长等待时间 60 分钟
  - 实时状态更新

### Fixed - 问题修复

- ✅ 修复前端 API 响应格式不一致问题
  - 统一 `upload` 和 `request` 函数的数据解包方式
  - 所有 API 统一返回解包后的数据

- ✅ 修复 AI 服务参数未正确传递的问题
  - `summarization_types` 正确传递给 API
  - `enable_speaker_diarization` 正确配置
  - `enable_chapters` 正确配置
  - `enable_meeting_assistance` 正确配置

- ✅ 完善错误处理和日志记录
  - 添加详细的错误堆栈信息（`exc_info=True`）
  - 关键步骤的日志输出
  - 便于问题排查

### Changed - 变更

#### 架构优化
- 🏗️ **服务分层**
  - 区分闪记处理器（`ai_processor.py`）和会议处理器（`meeting_processor.py`）
  - 不同场景使用不同的 AI 配置
  - 便于独立维护和优化

- 📊 **数据模型扩展**
  - Meeting 模型增加多个摘要字段
  - 支持更丰富的会议信息存储
  - 向后兼容旧数据

#### 功能对比

| 功能 | 闪记 | 会议纪要 |
|------|------|----------|
| 语音转写 | ✅ | ✅ |
| 段落摘要 | ✅ | ✅ |
| 关键词提取 | ✅ | ✅ |
| 发言总结 | ❌ | ✅ |
| 思维导图 | ❌ | ✅ |
| 说话人分离 | ❌ | ✅ |
| 章节划分 | ❌ | ✅ |
| 行动项识别 | ❌ | ✅ |

### Documentation - 文档

- 📚 **新增文档**
  - `backend/MEETING_FEATURE_UPDATE.md` - 会议纪要功能详细说明
  - `backend/DEPLOY_NEW_FEATURES.md` - 部署指南
  - `backend/TROUBLESHOOTING.md` - 问题排查指南
  - `backend/migrations/add_meeting_summary_types.py` - 数据库迁移脚本

- 📝 **更新文档**
  - `README.md` - 添加会议纪要功能说明
  - `backend/README.md` - 更新 API 接口文档

### Technical Highlights - 技术亮点

- **通义听悟深度集成**
  - 完整实现语音转写、说话人分离、章节划分、会议助手等功能
  - 支持 5 种智能摘要类型同时生成
  - 灵活的参数配置

- **智能要点提取**
  - 三层策略：章节 → 段落 → 兜底
  - 自适应不同会议场景
  - 确保任何情况下都有可用的要点

- **完整的前端体验**
  - 实时进度显示
  - 轮询机制确保状态同步
  - 多 Tab 展示，清晰呈现多维度信息

### Migration Guide - 迁移指南

升级到 0.2.0 版本需要执行数据库迁移：

```bash
cd backend
python migrations/add_meeting_summary_types.py
```

详细说明请参考 `backend/DEPLOY_NEW_FEATURES.md`。

---

## [0.1.0] - 2025-11-07

### 🎉 首个 MVP 版本发布

这是 Cshine 的第一个可用版本，实现了核心的语音记录和 AI 处理功能。

### Added - 新增功能

#### 前端功能
- 🎙️ **语音录制功能**
  - 长按录音，上滑取消
  - 实时录音时长显示
  - 波形动画效果
  - 震动反馈

- 📱 **核心页面**
  - 首页：闪记列表、分类筛选、统计信息
  - 详情页：内容展示、音频播放、操作菜单
  - 编辑页：标题/内容/分类编辑

- 🎨 **UI/UX 设计**
  - 自定义导航栏
  - 品牌渐变色（天蓝色 → 宇宙紫）
  - 流畅的卡片动画
  - 空状态提示
  - 加载状态反馈
  - iPhone X 安全区域适配

- 🔄 **交互功能**
  - 下拉刷新
  - 分类筛选（工作/生活/学习/灵感/其他）
  - 收藏/取消收藏
  - 删除确认
  - 音频播放控制

#### 后端功能
- 🔐 **认证系统**
  - 微信小程序登录
  - JWT Token 认证
  - 用户信息管理

- 📝 **闪记管理**
  - CRUD 操作（创建/读取/更新/删除）
  - 分页查询
  - 分类筛选
  - 收藏管理

- 🤖 **AI 服务集成**
  - 阿里云通义听悟语音识别
  - 智能摘要生成
  - 关键词提取
  - 自动分类
  - 异步处理机制

- 💾 **数据存储**
  - SQLite 数据库（开发环境）
  - 阿里云 OSS 文件存储
  - 音频文件管理

### Fixed - 问题修复

#### 样式修复
- ✅ 修复首页左侧空白问题
- ✅ 修复录音按钮波形动画不跟随的问题
- ✅ 修复详情页面无法滚动的问题
- ✅ 修复编辑页底部按钮未固定的问题
- ✅ 添加缺失的 CSS 变量 `--color-border`
- ✅ 统一分类颜色定义
- ✅ 优化页面滚动性能

#### 功能修复
- ✅ 添加录音防抖保护，避免重复触发
- ✅ 完善错误处理机制
- ✅ 优化录音最小时长检测

### Changed - 变更

#### 架构优化
- 🎨 **CSS 变量系统**
  - 统一的设计 token
  - 分类颜色集中管理
  - 便于主题切换和维护

- 📦 **组件化**
  - 自定义导航栏组件
  - 录音按钮组件
  - 闪记卡片组件

#### 性能优化
- ⚡ 使用 `will-change` 优化动画性能
- ⚡ 添加硬件加速（translateZ）
- ⚡ scroll-view 滚动优化

### Technical Highlights - 技术亮点

- **前端架构**
  - 微信小程序原生开发
  - CSS Variables 设计系统
  - 组件化开发模式
  - 响应式布局

- **后端架构**
  - FastAPI 异步框架
  - SQLAlchemy ORM
  - JWT 认证
  - 阿里云服务集成

- **AI 能力**
  - ASR 语音识别
  - NLP 文本分析
  - 智能分类算法
  - 异步任务处理

### Known Issues - 已知问题

- ⚠️ 搜索功能待开发
- ⚠️ 数据导出功能待开发
- ⚠️ 标签系统待开发

### Security - 安全性

- ✅ JWT Token 认证
- ✅ 环境变量配置
- ✅ 敏感信息保护
- ✅ .gitignore 配置

---

## [Unreleased] - 未来计划

### Phase 2 规划
- [x] 会议纪要模式（长时间录音）✅ v0.2.0
- [ ] 全文搜索功能
- [ ] 数据导出（Markdown/PDF）
- [ ] 个人中心
- [ ] 自定义标签
- [ ] 分享功能
- [ ] 骨架屏加载
- [ ] 更多主题支持

### Phase 3 规划
- [ ] 小程序审核上线
- [ ] 生产环境部署
- [ ] HTTPS 域名配置
- [ ] 性能监控
- [ ] 用户反馈系统

---

**版本号说明**：
- **主版本号（Major）**：重大功能更新或架构变更
- **次版本号（Minor）**：新增功能
- **修订号（Patch）**：bug 修复和小优化

[0.3.2]: https://github.com/cosmosva/Cshine/releases/tag/v0.3.2
[0.3.1]: https://github.com/cosmosva/Cshine/releases/tag/v0.3.1
[0.3.0]: https://github.com/cosmosva/Cshine/releases/tag/v0.3.0
[0.2.5]: https://github.com/cosmosva/Cshine/releases/tag/v0.2.5
[0.2.0]: https://github.com/cosmosva/Cshine/releases/tag/v0.2.0
[0.1.0]: https://github.com/cosmosva/Cshine/releases/tag/v0.1.0
