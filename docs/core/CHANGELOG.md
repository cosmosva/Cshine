# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.6] - 2025-01-14

### Fixed - Bug 修复 🐛

#### 数据库迁移脚本路径检测
- **问题**：开发环境数据库迁移失败，脚本查找 `app.db` 而实际文件是 `backend/cshine.db`
- **修复**：支持多路径检测逻辑
  - 优先查找 `backend/cshine.db`（项目根目录运行）
  - 其次查找 `cshine.db`（backend 目录运行）
  - 最后查找 `app.db`（默认位置）
- **改进**：添加详细日志输出路径检测结果
- **影响文件**：`backend/migrations/remove_conversational_summary_field.py`

## [0.9.5] - 2025-01-14

### Changed - 功能优化 🎨

#### AI 调度逻辑重构
- **核心变化**：实现两阶段处理架构（转录 → 总结）
  - 阶段1：通义听悟仅负责转录（转录文本 + 说话人分离）
  - 阶段2：LLM 负责总结（摘要/要点/行动项/标签/思维导图）
- **用户体验优化**：
  - 上传会议时不再选择 AI 模型，上传速度更快
  - 在详情页点击"立即生成"时选择 AI 模型
  - 用户可选择是否生成总结，更灵活
- **技术改进**：
  - 通义听悟关闭摘要/章节/行动项等智能功能，仅保留转录+说话人
  - 新增 LLM 总结服务 ([llm_summary_service.py](../../backend/app/services/llm_summary_service.py))
  - 重构会议处理器 ([meeting_processor.py](../../backend/app/services/meeting_processor.py))
  - 新增 API 接口：`POST /api/v1/meeting/{id}/generate-summary`
- **数据库变更**：
  - 移除 `meetings.conversational_summary` 字段（通义听悟发言总结）
  - 所有总结相关字段改为 LLM 生成
  - 迁移脚本：[remove_conversational_summary_field.py](../../backend/migrations/remove_conversational_summary_field.py)
- **影响文件**：
  - **新增**：`backend/app/services/llm_summary_service.py`
  - **新增**：`backend/migrations/remove_conversational_summary_field.py`
  - **新增**：`docs/features/FRONTEND_CHANGES_GUIDE_v095.md`
  - **修改**：`backend/app/models.py`
  - **修改**：`backend/app/schemas.py`
  - **修改**：`backend/app/services/meeting_processor.py`
  - **修改**：`backend/app/api/meeting.py`
  - **待修改**：前端文件（参见 [FRONTEND_CHANGES_GUIDE_v095.md](../features/FRONTEND_CHANGES_GUIDE_v095.md)）

### Deployment - 部署说明 📦
- **优先级**：建议 🟡
- **需要数据库迁移**：是（移除 conversational_summary 字段）
- **需要重启服务**：是
- **需要前端更新**：是
- **详细文档**：[DEPLOY_AI_SCHEDULING_20250114.md](../features/DEPLOY_AI_SCHEDULING_20250114.md)

## [0.9.4] - 2025-11-14

### Fixed - Bug 修复 🐛

#### AI 模型选择器数据解析
- **问题**：模型选择器无法加载模型列表，所有属性显示 undefined
- **原因**：`request.js` 已将响应解包一层（返回 `res.data.data`），但组件代码期望完整响应
- **修复**：调整数据解析逻辑，直接从返回值中获取 `items`
- **影响文件**：`miniprogram/components/ai-model-picker/ai-model-picker.js`

## [0.9.3] - 2025-11-14

### Fixed - Bug 修复 🐛

#### AI 模型 API 数据格式
- **问题**：前端期望 `res.data.items`，后端返回的是数组
- **修复**：后端返回标准列表格式 `{ items: [...], total: N }`
- **改进**：前端增加详细日志便于调试
- **影响文件**：
  - `backend/app/api/ai_models.py`
  - `miniprogram/components/ai-model-picker/ai-model-picker.js`

## [0.9.2] - 2025-11-14

### Fixed - Bug 修复 🐛

#### API 路由 404 错误
- **问题**：所有 AI 模型相关 API 返回 404 Not Found
- **原因**：路由定义时重复添加了 `/api` 前缀
- **修复**：移除重复前缀，确保路径正确
- **正确路径**：
  - `/api/v1/admin/login` ✅
  - `/api/v1/admin/ai-models` ✅
  - `/api/v1/ai-models/available` ✅
- **影响文件**：
  - `backend/app/api/admin.py`
  - `backend/app/api/ai_models.py`
  - `backend/app/api/ai_prompts.py`

## [0.9.1] - 2025-11-13

### Fixed - Bug 修复 🐛

#### 会议详情页 showModal 错误
- **问题**：`TypeError: showModal is not a function`
- **原因**：`utils/toast.js` 只导出了 `showConfirm`，但 `detail.js` 引用了 `showModal`
- **修复**：统一使用 `showConfirm` 函数
- **影响文件**：
  - `miniprogram/pages/meeting/detail.js`
  - `miniprogram/utils/toast.js`

## [0.9.0] - 2025-11-13

### Added - 小程序端 AI 模型选择 📱

#### 核心功能
- 🎯 **AI 模型选择器组件**
  - 底部弹窗式设计
  - 显示可用 AI 模型列表（从后端动态获取）
  - 支持选择/取消操作
  - 显示默认模型标记
  - 空状态和加载状态提示
  
- 📱 **会议创建集成**
  - 上传音频文件时可选择 AI 模型
  - 流程：选择文件 → 选择知识库 → 选择 AI 模型 → 上传
  - 自动传递 `ai_model_id` 到后端
  - 选择的模型会被保存到会议记录中
  
- 🎤 **闪记录音集成**
  - 录音完成后可选择 AI 模型
  - 流程：录音 → 选择 AI 模型 → 创建闪记
  - 支持使用不同模型处理不同的闪记

#### 技术实现
- **组件化设计**
  - `ai-model-picker` 独立可复用组件
  - 使用微信小程序组件系统
  - 支持事件通信（confirm/close）
  
- **API 集成**
  - 新增 `getAvailableModels()` API 函数
  - 调用 `/api/v1/ai-models/available` 获取模型列表
  - 自动过滤：只显示启用的模型
  
- **用户体验**
  - 现代化的 UI 设计（渐变色、圆角、阴影）
  - 平滑的动画过渡（0.3s cubic-bezier）
  - 清晰的选中状态反馈（蓝色高亮、对勾图标）
  - 触摸反馈（点击时背景变化）

#### 新增文件
- `miniprogram/components/ai-model-picker/ai-model-picker.js` - 组件逻辑
- `miniprogram/components/ai-model-picker/ai-model-picker.json` - 组件配置
- `miniprogram/components/ai-model-picker/ai-model-picker.wxml` - 组件模板
- `miniprogram/components/ai-model-picker/ai-model-picker.wxss` - 组件样式

#### 修改文件
- `miniprogram/utils/api.js` - 添加获取模型列表 API
- `miniprogram/pages/meeting/list.js` - 集成模型选择器
- `miniprogram/pages/meeting/list.json` - 注册组件
- `miniprogram/pages/meeting/list.wxml` - 添加组件标签
- `miniprogram/pages/index/index.js` - 集成模型选择器
- `miniprogram/pages/index/index.json` - 注册组件
- `miniprogram/pages/index/index.wxml` - 添加组件标签

#### 用户使用流程

**会议创建**：
1. 点击上传音频文件
2. 选择文件（支持 mp3、m4a、wav）
3. 选择目标知识库
4. 选择 AI 模型（或使用默认）
5. 开始上传和处理

**闪记录音**：
1. 长按录音按钮录音
2. 松开停止录音
3. 选择 AI 模型（或使用默认）
4. 开始上传和 AI 处理

#### 默认行为
- 提供"默认（规则分类）"选项
- 不选择 AI 模型时使用规则分类器
- 完全向后兼容现有功能
- 管理员未配置模型时自动降级

#### 提供商映射
- `openai` → OpenAI
- `anthropic` → Anthropic
- `doubao` → 字节豆包
- `qwen` → 阿里通义

---

## [0.8.0] - 2025-11-13

### Added - Web 管理后台 🎨

#### 核心功能
- 🎨 **轻量级 Web 管理后台界面**
  - 使用 Bootstrap 5 构建现代化 UI
  - 响应式设计，支持移动端访问
  - 清爽的渐变色主题
  
- 🤖 **AI 模型可视化管理**
  - 添加、编辑、删除 AI 模型
  - 模型列表展示（名称、提供商、状态、默认标记）
  - 模型连接测试功能
  - 支持设置默认模型和启用/禁用状态
  
- 📝 **提示词模板管理**
  - 查看系统预置的提示词模板
  - 按场景分类（会议摘要、闪记分类、行动项提取等）
  - 支持查看模板详细内容
  
- 🔐 **安全认证**
  - JWT Token 认证机制
  - 管理员登录/登出
  - Token 自动续期
  - 登录状态检查

#### 技术实现
- **前端技术栈**
  - HTML5 + Vanilla JavaScript
  - Bootstrap 5.3.0（UI 框架）
  - Font Awesome 6.4.0（图标库）
  - 使用 CDN 加速资源加载
  
- **后端集成**
  - FastAPI StaticFiles 挂载静态文件
  - 与现有 API 完美集成
  - 统一的 CORS 配置
  
- **用户体验**
  - 单页应用（SPA）设计
  - 平滑的页面切换动画
  - 友好的错误提示
  - 加载状态反馈

#### 访问地址
- **本地开发**：`http://localhost:8000/static/admin/login.html`
- **生产环境**：`https://your-domain.com/static/admin/login.html`
- **默认账号**：`admin` / `admin123456`

#### 新增文件
- `backend/static/admin/login.html` - 管理后台登录页面
- `backend/static/admin/index.html` - 管理后台主页面
- `backend/static/admin/app.js` - 前端业务逻辑
- `backend/static/admin/README.md` - Web 管理后台使用文档

#### 修改文件
- `backend/main.py` - 添加静态文件服务支持

#### 安全建议
1. 首次部署后立即修改默认密码
2. 生产环境必须使用 HTTPS
3. 配置防火墙或 Nginx 限制访问 IP
4. 定期更新系统和依赖
5. 确保 API Key 的安全存储

#### 后续计划
- [ ] 提示词模板的完整 CRUD 操作
- [ ] 管理员账号管理功能
- [ ] 系统日志查看功能
- [ ] 使用统计和成本监控
- [ ] 导出/导入配置功能

---

## [0.7.0] - 2025-11-13

### Changed - AI 调用逻辑重构 🔄

#### 核心改造
- 🤖 **LLM 分类器**
  - 创建 `LLMClassifier` 基于统一 LLM 层的智能分类器
  - 支持使用可配置的 AI 模型进行内容分类
  - 支持智能关键词提取
  - 支持行动项识别和提取
  - 自动降级机制：LLM 调用失败时自动降级到规则分类器

- 📊 **AI 处理器改造**
  - `ai_processor.py` (闪记处理) 支持 AI 模型选择
  - `meeting_processor.py` (会议处理) 支持 AI 模型选择
  - 条件使用 LLM：指定 AI 模型时使用 LLM，否则使用传统规则分类
  - 完整的错误处理和降级逻辑

- 📦 **Schema 更新**
  - `FlashCreate` 添加 `ai_model_id` 字段（可选）
  - `MeetingCreate` 添加 `ai_model_id` 字段（可选）
  - 向后兼容：不传 `ai_model_id` 时使用原有的规则分类

- 🔧 **API 增强**
  - `POST /api/v1/flash/create` - 支持传递 `ai_model_id`
  - `POST /api/v1/meeting/create` - 支持传递 `ai_model_id`
  - `POST /api/v1/meeting/{id}/reprocess` - 使用会议记录中保存的 AI 模型

#### 技术特性
- ✅ 向后兼容：不传 `ai_model_id` 时完全使用原有逻辑
- ✅ 灵活降级：LLM 调用失败自动降级到规则方法，不影响用户体验
- ✅ 统一接口：所有 AI 功能通过统一的 LLM 工厂调用
- ✅ 清晰日志：每个步骤都有详细的日志记录

#### 新增文件
- `backend/app/services/llm_classifier.py` - 基于 LLM 的智能分类器

#### 优化点
- 代码结构更清晰，易于扩展新的 AI 功能
- 支持多种 AI 模型，用户可自由选择
- 完善的错误处理，提高系统稳定性

---

## [0.6.0] - 2025-11-13

### Added - AI 模型统一管理系统 🤖

#### 核心功能
- 🤖 **多 AI 模型支持**
  - 支持 OpenAI (GPT)、Anthropic (Claude)、字节豆包、阿里通义千问
  - 统一的 LLM 调用接口，屏蔽底层差异
  - 支持动态配置和切换模型
  - 支持测试模型连接

- 👨‍💼 **管理员系统**
  - 独立的管理员账号体系
  - 基于 JWT 的认证机制
  - 支持超级管理员权限
  - 默认账号：admin / admin123456

- 📝 **提示词模板管理**
  - 支持多场景提示词（会议摘要、闪记分类、行动项提取等）
  - 支持变量占位符
  - 可设置默认模板

- 👤 **用户端功能**
  - 查看可用的 AI 模型列表
  - 选择不同模型进行对话
  - 自定义温度、最大 token 等参数

#### 数据库变更
- 新增 `ai_models` 表 - AI 模型配置
- 新增 `ai_prompts` 表 - 提示词模板
- 新增 `admin_users` 表 - 管理员账号
- `flashes` 表新增 `ai_model_id` 字段
- `meetings` 表新增 `ai_model_id` 字段

#### API 接口
**管理员接口**：
- `POST /api/v1/api/admin/login` - 管理员登录
- `GET /api/v1/api/admin/me` - 获取当前管理员信息
- `GET /api/v1/api/admin/ai-models` - 获取 AI 模型列表
- `POST /api/v1/api/admin/ai-models` - 创建 AI 模型
- `PUT /api/v1/api/admin/ai-models/{id}` - 更新模型配置
- `DELETE /api/v1/api/admin/ai-models/{id}` - 删除模型
- `POST /api/v1/api/admin/ai-models/{id}/test` - 测试模型连接
- `GET /api/v1/api/admin/ai-prompts` - 获取提示词列表
- `POST /api/v1/api/admin/ai-prompts` - 创建提示词
- `PUT /api/v1/api/admin/ai-prompts/{id}` - 更新提示词
- `DELETE /api/v1/api/admin/ai-prompts/{id}` - 删除提示词

**用户接口**：
- `GET /api/v1/api/ai-models` - 获取可用模型列表
- `POST /api/v1/api/ai-models/chat` - AI 对话

#### 技术实现
- 抽象了 `BaseLLM` 基类，统一接口
- 实现了各厂商的适配器（OpenAI、Anthropic、豆包、通义千问）
- LLM 工厂模式，根据配置动态创建实例
- 使用 bcrypt 加密管理员密码

#### 文件变更
**新增文件**：
- `backend/app/services/llm/base.py` - LLM 基类
- `backend/app/services/llm/openai_llm.py` - OpenAI 适配器
- `backend/app/services/llm/anthropic_llm.py` - Claude 适配器
- `backend/app/services/llm/doubao_llm.py` - 豆包适配器
- `backend/app/services/llm/qwen_llm.py` - 通义千问适配器
- `backend/app/services/llm/factory.py` - LLM 工厂
- `backend/app/api/admin.py` - 管理员 API
- `backend/app/api/ai_models.py` - AI 模型管理 API
- `backend/app/api/ai_prompts.py` - 提示词管理 API
- `backend/migrations/add_ai_models_and_prompts.py` - 数据库迁移脚本
- `backend/init_ai_system.py` - 初始化脚本

**修改文件**：
- `backend/app/models.py` - 新增 AI 相关模型
- `backend/app/schemas.py` - 新增 AI 相关 schemas
- `backend/app/dependencies.py` - 新增管理员认证依赖
- `backend/app/api/__init__.py` - 注册新路由
- `backend/config.py` - 新增管理员配置
- `backend/requirements.txt` - 新增 bcrypt 依赖

#### 部署文档
- 📋 `docs/features/DEPLOY_AI_MODELS_SYSTEM_20251113.md`
- 更新优先级：🟡 建议
- 预计停机时间：< 5 分钟

---

## [0.5.20] - 2025-11-13

### Fixed - 上传流程修复 🐛

#### 修复的问题
- 🐛 **上传后页面卡住**
  - 问题：上传成功后显示"正在上传..."，0%，无法跳转
  - 原因：上传成功后只刷新列表，没有跳转到详情页
  - 修复：上传成功后 1 秒自动跳转到会议详情页

- 🐛 **仍然自动触发处理**
  - 问题：上传后直接处理，没有出现"立即生成"按钮
  - 原因：`/audio-and-meeting` 接口中仍有自动处理代码
  - 修复：注释掉该接口的自动处理逻辑

#### 后端改动
- 📦 **backend/app/api/upload.py**
  - 注释掉第 228-230 行的自动 AI 处理
  - 修改返回消息："上传成功，请点击「立即生成」开始处理"
  - 返回数据添加 `id` 字段，方便前端获取 meeting_id

#### 前端改动
- 📱 **miniprogram/pages/meeting/list.js**
  - 上传成功提示改为"上传成功！"
  - 添加 1 秒延迟后自动跳转
  - 使用 `wx.navigateTo` 跳转到详情页
  - 清除上传状态标志

### Technical - 技术细节

**完整的上传流程**：
```
1. 选择文件 → 提取时长
2. 选择知识库
3. 上传到 OSS → 创建会议记录（pending 状态）
4. 显示"上传成功！" → 1 秒后跳转
5. 详情页显示「✨ 立即生成」按钮
6. 用户点击 → 开始 AI 处理
```

**修复前后对比**：

| 状态 | 修复前 | 修复后 |
|------|--------|--------|
| 上传提示 | "上传成功，正在AI处理..." | "上传成功！" |
| 页面跳转 | ❌ 卡住在上传页 | ✅ 自动跳转详情页 |
| AI 处理 | ❌ 自动触发 | ✅ 手动触发 |
| 用户体验 | ⏳ 等待不明确 | ✨ 清晰的操作引导 |

---

## [0.5.19] - 2025-11-13

### Changed - 会议处理交互优化 ✨

#### 手动触发 AI 处理
- 🎯 **上传后不自动处理**
  - 上传录音后不再自动启动 AI 转录
  - 保持 `pending` 状态，等待用户触发
  - 节省 AI 资源，给用户确认时间

- ✨ **立即生成按钮**
  - 会议详情页新增"立即生成"按钮
  - 点击后确认对话框，告知预计处理时间
  - 状态变为 `processing`，显示处理中提示
  - 自动轮询状态，完成后刷新页面

- 🔄 **智能状态轮询**
  - 每 3 秒检查一次处理状态
  - 完成或失败时停止轮询
  - 页面卸载时自动清除定时器
  - 处理完成后自动刷新内容

- 🎨 **精美 UI 设计**
  - **立即生成**：蓝紫渐变按钮 + 阴影效果
  - **处理中**：灰色背景 + 旋转动画图标
  - **重新处理**：紫色渐变按钮（completed/failed 状态显示）
  - 按钮点击有缩放反馈

#### 后端改动
- 📦 **修改创建会议 API**
  - 注释掉自动触发 AI 处理的代码
  - 返回消息改为"请点击「立即生成」开始处理"
  - 会议初始状态保持 `pending`

- 🔌 **复用 reprocess API**
  - 利用现有的 `/api/v1/meeting/{meeting_id}/reprocess` 接口
  - 既可用于首次处理，也可用于重新处理
  - 统一的处理逻辑

#### 前端改动
- 📱 **会议详情页（miniprogram/pages/meeting/detail.*）**
  - 新增 `startProcessing()` 方法 - 触发首次处理
  - 新增 `startStatusPolling()` 方法 - 开始状态轮询
  - 新增 `checkProcessingStatus()` 方法 - 检查处理状态
  - 优化 `reprocessMeeting()` 方法 - 统一轮询逻辑
  - 页面卸载时清除轮询定时器

- 🎨 **UI 状态管理**
  - `pending` 状态：显示"立即生成"按钮
  - `processing` 状态：显示"处理中"提示 + 旋转动画
  - `completed`/`failed` 状态：显示"重新处理"按钮

### Technical - 技术细节

**状态流转**：
```
上传音频 → pending（待处理）
  ↓ 点击"立即生成"
processing（处理中）→ 每 3 秒轮询
  ↓ AI 处理完成
completed（已完成）→ 显示内容 + "重新处理"按钮
```

**轮询机制**：
- 定时器：`setInterval(checkStatus, 3000)`
- 状态变化后停止轮询
- 页面卸载时清除定时器
- 避免内存泄漏

**用户体验**：
- ✅ 上传即刻返回，无需等待
- ✅ 手动控制处理时机
- ✅ 实时进度反馈
- ✅ 处理完成自动刷新
- ✅ 流畅的动画效果

---

## [0.5.18] - 2025-11-13

### Changed - 项目结构重构 🏗️

#### 目录结构调整
- 📁 **小程序代码统一管理**
  - 创建 `miniprogram/` 目录
  - 移动所有小程序相关文件到 `miniprogram/`
  - 为未来多端开发（Web端）做准备
  
- 🔄 **移动的文件和目录**
  - 配置文件：`app.js`, `app.json`, `app.wxss`, `project.config.json`, `project.private.config.json`, `sitemap.json`
  - 代码目录：`pages/`, `components/`, `utils/`, `assets/`, `styles/`
  
- 📦 **保持不变的内容**
  - `backend/` - 后端服务
  - `docs/` - 项目文档
  - `README.md` - 项目说明
  - `.cursorrules` - 开发规则
  - 其他配置文件

#### 新的项目结构
```
Cshine/
├── miniprogram/          # 小程序端（新增）
│   ├── app.js
│   ├── app.json
│   ├── app.wxss
│   ├── pages/
│   ├── components/
│   ├── utils/
│   ├── assets/
│   ├── styles/
│   └── project.config.json
├── backend/              # 后端服务
├── docs/                 # 项目文档
└── README.md
```

#### 优势
- ✅ 清晰的代码组织，小程序代码统一在 `miniprogram/` 目录
- ✅ 为未来 Web 端开发预留空间（`web/` 目录）
- ✅ 使用 `git mv` 保留完整的 Git 历史记录
- ✅ 不影响现有功能，向后兼容

### Technical - 技术细节
- 使用 `git mv` 命令移动文件，保留 Git 历史
- 微信开发者工具需要重新打开 `miniprogram/` 目录
- 小程序内部的相对路径无需修改

---

## [0.5.17] - 2025-11-12

### Fixed - 部署脚本修复

#### 数据库迁移脚本 🔧
- 🐛 **修复 DATABASE_URL 解析**
  - 问题：迁移脚本尝试访问不存在的 `settings.DB_HOST` 等字段
  - 原因：服务器配置使用 `DATABASE_URL` 连接字符串
  - 修复：使用 `urllib.parse.urlparse` 解析 PostgreSQL URL
  - 支持：自动提取 host, port, database, user, password

- ✅ **改进错误处理**
  - 初始化 `conn = None` 和 `cursor = None`
  - 避免 `UnboundLocalError` 异常
  - 更清晰的错误信息

#### 部署脚本优化 📦
- 🔧 **修复 Python 命令**
  - 服务器环境使用 `python3.11` 而不是 `python`
  - 确保使用正确的 Python 版本执行迁移

- 📝 **更新服务器端脚本**
  - 更新版本号 v0.5.5 → v0.5.17
  - 添加详细的使用说明
  - 改进更新摘要信息

### Changed - 改进

#### 部署文档 📖
- 📋 **完善部署说明**
  - 说明数据库迁移可在 cshine 用户下执行
  - 只有重启服务需要 sudo 权限
  - 提供两种执行方式

## [0.5.16] - 2025-11-12

### Fixed - 部署脚本修复

- 🔧 **更新部署脚本使用 python3.11**
  - 服务器环境需要明确使用 `python3.11` 命令
  - 修改数据库迁移脚本执行命令

## [0.5.13] - 2025-11-11

### 🎉 重大修复 - 通义听悟摘要功能完全正常工作

经过深入调试和多次迭代，终于完全修复了通义听悟摘要功能，现在能正确获取并保存所有类型的摘要数据！

### Fixed - 问题修复

#### 通义听悟摘要数据解析 🔧
- 🐛 **修复数据格式解析错误**
  - 问题：之前假设 `Summarization` 是数组，实际是字典
  - 修复：正确解析字典格式的摘要数据
  - 键名：`ParagraphSummary`、`ConversationalSummary`、`MindMapSummary`

- 📋 **修复摘要类型映射**
  - 段落摘要：`ParagraphSummary` → `summary`
  - 发言总结：`ConversationalSummary` (列表) → `conversational_summary` (JSON)
  - 思维导图：`MindMapSummary` (列表) → `mind_map` (JSON)

- ✅ **添加 summarization_enabled 标志**
  - 根据阿里云官方文档，必须同时设置：
    1. `summarization_enabled = True`（顶层开关）
    2. `Summarization.Types`（具体类型）
  - 同样修复了 `meeting_assistance_enabled` 和 `auto_chapters_enabled`

- 🔍 **增强调试日志**
  - 详细记录数据类型、键名、内容预览
  - 便于快速定位数据格式问题

### Added - 新增功能

#### 会议重新处理功能 🔄
- 🎯 **一键重新处理**
  - 在会议详情页添加「重新处理」按钮
  - 支持为旧会议生成新的摘要类型
  - 确认对话框，避免误操作
  - 处理完成后自动刷新页面

- 🛠️ **调试和修复工具**
  - 修复后端代码后可重新处理会议
  - 调试通义听悟返回的数据格式
  - 验证摘要功能是否正常工作

### Improved - 改进优化

#### 上传功能优化 📤
- ⏱️ **超时控制**：60秒后自动中止上传任务
- 🎯 **任务管理**：保存 uploadTask 对象，支持 abort
- 💬 **友好提示**：针对不同错误类型显示不同提示
- 📊 **进度监听**：为未来的进度条功能做准备

#### 参数处理优化 🔧
- 📝 **folder_id 类型转换**
  - 后端接收为字符串，手动转换为整数或 None
  - 前端只在有值时才传递，且转换为字符串
  - 正确处理未分类（folder_id=null）的情况

- 🏷️ **title 参数优先级**
  - 优先使用前端传递的 title
  - 避免使用微信处理后的临时文件名
  - 确保会议标题正确显示

### Technical - 技术细节

#### 通义听悟数据格式（已验证）
```json
{
  "Summarization": {
    "ParagraphSummary": "段落摘要文本...",
    "ParagraphTitle": "标题",
    "ConversationalSummary": [
      {
        "SpeakerId": "1",
        "SpeakerName": "发言人1",
        "Summary": "发言总结..."
      }
    ],
    "MindMapSummary": [
      {
        "Title": "主题",
        "Topic": [...]
      }
    ]
  }
}
```

#### 测试结果 ✅
- ✅ conversational_summary: 581 chars
- ✅ mind_map: 1,498 chars  
- ✅ summary: 159 chars

**通义听悟摘要功能现已完全正常工作！** 🎉

---

## [0.5.12] - 2025-11-11

### Added - 新增功能

#### 会议重新处理功能 🔄
- 添加前端 `reprocessMeeting` API 接口
- 在会议详情页添加「重新处理」按钮
- 点击后弹窗确认，避免误操作
- 处理完成后自动刷新页面

---

## [0.5.11] - 2025-11-11

### Fixed - 问题修复

#### 通义听悟摘要功能启用 🔧
- 添加 `summarization_enabled = True`
- 添加 `meeting_assistance_enabled = True`
- 添加 `auto_chapters_enabled = True`
- 更新日志输出，明确显示 enabled 标志

---

## [0.5.10] - 2025-11-11

### ✨ 功能增强 - 音频波形可视化播放器

这是一个重要的体验优化版本，为会议详情页实现了音频波形可视化播放器，大幅提升音频播放体验。

### Added - 新增功能

#### 音频波形播放器 ✨
- 🎵 **真实音频波形可视化**
  - 使用 librosa 提取音频实际波形数据
  - Canvas 实时绘制波形图
  - 已播放部分红色高亮，未播放部分黑色
  - 波形数据缓存到数据库，避免重复提取

- ⚡ **增强播放控制**
  - 倍速播放：支持 0.5x / 1.0x / 1.5x / 2.0x
  - 快进/快退：一键跳转 ±15 秒
  - 时间显示：当前时间 / 总时长
  - 播放进度与波形实时同步

- 🎨 **优雅的 UI 设计**
  - 独立的波形播放器组件
  - 现代化的控制按钮布局
  - 流畅的动画效果
  - 响应式设计，适配不同设备

### Changed - 优化

- 🔄 **替换原有音频播放器**
  - 移除旧的简单进度条播放器
  - 集成新的波形可视化播放器
  - 保持向后兼容，没有波形数据时优雅降级

- 📦 **性能优化**
  - 波形数据缓存机制（首次提取 5-15 秒，后续秒级响应）
  - Canvas 绘制优化（使用 requestAnimationFrame）
  - 波形数据降采样到 800 个点

### Technical - 技术细节

#### 后端
- 新增 `backend/app/services/waveform_service.py` - 波形提取服务
- 新增 `GET /api/v1/meeting/{meeting_id}/waveform` API 接口
- 新增 `meetings.waveform_data` 字段（TEXT，存储 JSON 格式波形数据）
- 新增依赖：`librosa==0.10.2`, `numpy==1.26.4`

#### 前端
- 新增 `components/waveform-player/` - 波形播放器组件
  - Canvas 波形绘制
  - 音频播放控制
  - 进度同步
  - 倍速/快进快退功能
- 更新 `pages/meeting/detail.*` - 集成波形播放器
- 新增 `utils/api.js::getMeetingWaveform` - 波形数据 API 调用

#### 数据库迁移
- PostgreSQL: `backend/migrations/add_waveform_data.py`
- SQLite: `backend/migrations/add_waveform_data_sqlite.py`

### Documentation - 文档

- 📝 新增部署文档：`docs/features/DEPLOY_WAVEFORM_PLAYER_20251111.md`
  - 详细的部署步骤
  - 依赖安装说明
  - 验证方法
  - 回滚方案
  - 注意事项

---

## [0.5.6] - 2025-11-10

### Fixed - 修复

- 🐛 修复知识库选择器 Modal 缺少 `wx:if` 导致意外显示的问题
- 🐛 修复移动会议后原列表未更新的问题
- 🐛 修复上传文件和会议操作共用选择器导致的冲突
- 🐛 删除旧的未使用的知识库选择器代码

### Changed - 优化

- 🎨 优化 Modal 布局，底部按钮固定不滚动
- 🎨 使用 `folder.png` 图标替代 emoji，统一视觉风格
- 📝 新增版本号自动管理规则
- 📝 新增资源文件复用规则

### Technical - 技术细节

- 为知识库选择器添加 `wx:if` 条件控制
- 移动会议后立即从当前列表中过滤掉已移动项
- 分离上传文件和会议操作的知识库选择器
- 使用 Flexbox 布局优化 Modal 结构
- 更新 `.cursorrules` 开发规范

---

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
