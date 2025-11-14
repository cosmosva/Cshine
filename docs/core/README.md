# Cshine 微信小程序

[![Version](https://img.shields.io/badge/version-0.9.1-blue.svg)](https://github.com/cosmosva/Cshine)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![WeChat](https://img.shields.io/badge/WeChat-MiniProgram-07C160.svg)](https://mp.weixin.qq.com/)

> **Let Your Ideas Shine. ✨**
> AI 驱动的语音记录与灵感管理工具
>
> **当前版本**: v0.9.1 | **发布日期**: 2025-11-13

## 📱 项目简介

Cshine 是一款基于微信小程序的智能语音记录工具，帮助用户随时随地捕捉灵感、记录想法。通过 AI 技术自动将语音转为文字并生成智能摘要，让每个想法都能被轻松管理和回顾。

### 核心功能

#### 闪记功能
- 🎙️ **闪记（Voice Flash）**：长按录音，即刻记录灵感 ✅
- 📝 **智能转写**：自动将语音转为文字（阿里云通义听悟）✅
- 🧠 **AI 摘要**：自动生成内容摘要和关键词 ✅
- 🏷️ **智能分类**：自动识别内容类别（工作/生活/学习/灵感/其他）✅
- 🔍 **快速检索**：按分类筛选历史记录 ✅
- ⭐ **收藏管理**：标记重要内容，快速访问 ✅
- 📖 **详情查看**：查看完整内容、播放音频 ✅
- ✏️ **编辑功能**：修改标题、内容和分类 ✅
- 🗑️ **删除功能**：删除不需要的记录 ✅

#### 会议纪要功能
- 📋 **会议上传**：上传会议音频文件（支持 mp3/m4a/wav，最大 500MB）✅
- 🎯 **智能转写**：自动将会议音频转为文字 ✅
- 📑 **章节划分**：自动识别不同议题，生成章节目录 ✅
- 👥 **说话人分离**：自动区分不同发言人 ✅
- 💡 **要点提取**：按章节或发言人提取会议讨论要点 ✅
- ✅ **行动项识别**：智能识别待办事项和负责人 ✅
- 📝 **5种智能摘要**：段落摘要、发言总结、思维导图、问答总结 ✅
- 📄 **结构化纪要**：生成完整的会议纪要文档 ✅
- 🔄 **实时进度**：显示 AI 处理进度 ✅
- 📊 **多维展示**：摘要、要点、行动项、全文分 Tab 展示 ✅
- 🗂️ **知识库管理**：支持创建文件夹分类管理会议 ✅
- 🔄 **会议操作**：复制、移动、重新处理 ✅

#### AI 模型管理系统 ✨ 最新
- 🤖 **多模型支持**：OpenAI (GPT)、Anthropic (Claude)、字节豆包、阿里通义千问 ✅
- 🎯 **模型选择**：会议和闪记创建时可选择不同 AI 模型 ✅
- 🔧 **Web 管理后台**：可视化配置和管理 AI 模型 ✅
- 📝 **提示词管理**：支持自定义不同场景的提示词模板 ✅
- 🛡️ **自动降级**：AI 模型调用失败时自动降级到规则分类器 ✅
- 👨‍💼 **管理员系统**：独立的管理员账号体系和 JWT 认证 ✅

## 🎨 设计特色

- **三 Tab 导航**：清晰的功能分区
  - 📚 知识库：会议纪要管理
  - ⚡ Cshine：快速闪记录制
  - 👤 我的：个人中心和设置
- **极简设计**：清爽的界面，专注核心体验
- **渐变配色**：天蓝色 + 宇宙紫的品牌渐变色
- **流畅动画**：呼吸动画、波形效果、卡片交互
- **细节打磨**：震动反馈、加载状态、空状态设计

## 🛠️ 技术栈

### 前端
- **框架**：微信小程序原生开发
- **组件化**：自定义组件（导航栏、录音按钮、闪记卡片）
- **样式系统**：CSS Variables + WXSS
- **状态管理**：全局 App 实例 + 页面级状态
- **网络请求**：封装的 wx.request + JWT 认证

### 后端
- **语言**：Python 3.11+
- **框架**：FastAPI
- **数据库**：SQLite（开发环境）/ PostgreSQL（生产环境）
- **ORM**：SQLAlchemy
- **认证**：JWT Token
- **文件存储**：阿里云 OSS

### AI 服务
- **语音识别**：阿里云通义听悟（ASR）
- **文本分析**：通义听悟（摘要、关键词）
- **智能分类**：规则分类器 + LLM 智能分类
- **多模型支持**：OpenAI、Anthropic、字节豆包、阿里通义
- **统一接口**：LLM 抽象层 + 工厂模式
- **异步处理**：Python Threading

## 📁 项目结构

```
Cshine/
├── miniprogram/            # 小程序端 ✨
│   ├── app.js              # 小程序入口
│   ├── app.json            # 全局配置
│   ├── app.wxss            # 全局样式
│   ├── components/         # 组件目录
│   │   ├── navigation-bar/ # 导航栏组件
│   │   ├── record-button/  # 录音按钮组件（支持长按、波形动画）
│   │   ├── flash-card/     # 闪记卡片组件
│   │   ├── upload-modal/   # 上传进度模态框
│   │   └── ai-model-picker/# AI 模型选择器组件 ✨ 新增
│   ├── pages/              # 页面目录
│   │   ├── index/          # Cshine 主页（列表、录音、筛选）✨ Tab
│   │   ├── detail/         # 闪记详情页（查看、播放、操作）
│   │   ├── edit/           # 编辑页（修改内容）
│   │   ├── meeting/        # 会议纪要页面
│   │   │   ├── list/       # 知识库页面（会议列表）✨ Tab
│   │   │   └── detail/     # 会议详情
│   │   └── profile/        # 我的页面（个人中心）✨ Tab
│   ├── styles/             # 样式系统
│   │   ├── variables.wxss  # 全局变量（色彩、尺寸等）
│   │   └── common.wxss     # 通用样式（工具类）
│   ├── utils/              # 工具类
│   │   ├── api.js          # API 接口封装
│   │   ├── request.js      # 网络请求封装
│   │   ├── config.js       # 配置文件
│   │   ├── format.js       # 格式化工具
│   │   ├── storage.js      # 本地存储
│   │   └── toast.js        # 提示工具
│   └── project.config.json # 小程序配置
├── web/                    # Web 端（待开发）
├── backend/                # 后端服务
│   ├── app/                # 应用目录
│   │   ├── api/            # API 路由
│   │   │   ├── admin.py    # 管理员 API ✨
│   │   │   ├── ai_models.py# AI 模型管理 API ✨
│   │   │   ├── ai_prompts.py# 提示词管理 API ✨
│   │   │   ├── auth.py     # 认证 API
│   │   │   ├── flash.py    # 闪记 API
│   │   │   ├── meeting.py  # 会议 API
│   │   │   ├── folder.py   # 知识库 API
│   │   │   └── upload.py   # 上传 API
│   │   ├── models.py       # 数据模型（含 AI 模型配置）✨
│   │   ├── schemas.py      # 数据验证
│   │   ├── database.py     # 数据库连接
│   │   ├── dependencies.py # 依赖注入（含管理员认证）✨
│   │   ├── services/       # 业务服务
│   │   │   ├── llm/        # LLM 统一调用层 ✨
│   │   │   │   ├── base.py          # LLM 基类
│   │   │   │   ├── factory.py       # LLM 工厂
│   │   │   │   ├── openai_llm.py    # OpenAI 适配器
│   │   │   │   ├── anthropic_llm.py # Anthropic 适配器
│   │   │   │   ├── doubao_llm.py    # 豆包适配器
│   │   │   │   └── qwen_llm.py      # 通义适配器
│   │   │   ├── llm_classifier.py    # LLM 智能分类器 ✨
│   │   │   ├── tingwu_service.py    # 通义听悟服务
│   │   │   ├── classifier.py        # 规则分类器
│   │   │   ├── ai_processor.py      # 闪记 AI 处理器
│   │   │   └── meeting_processor.py # 会议 AI 处理器
│   │   └── utils/          # 工具函数
│   ├── static/             # 静态文件
│   │   └── admin/          # Web 管理后台 ✨
│   │       ├── login.html
│   │       ├── index.html
│   │       └── app.js
│   ├── migrations/         # 数据库迁移脚本 ✨
│   ├── main.py             # 入口文件
│   ├── config.py           # 配置管理
│   ├── requirements.txt    # 依赖列表
│   └── README.md           # 后端文档
├── docs/                   # 项目文档
│   ├── core/               # 核心文档
│   ├── deployment/         # 部署文档
│   └── features/           # 功能文档
└── README.md               # 项目说明
```

## 🚀 快速开始

### ⚠️ 开发规范（必读）

**提交代码前请先阅读**：
- 📖 [开发规范](DEVELOPMENT_GUIDE.md) - 完整的开发规范和最佳实践
- ⚡ [快速检查清单](../../QUICK_CHECKLIST.md) - 打印出来贴在显示器旁边！

**核心规则**：
- ✅ **后端功能更新 = 必须创建部署文档**（`docs/features/DEPLOY_*.md`）
- ✅ 使用模板：`.github_docs_template.md`
- ✅ 标注优先级：必须🔴/建议🟡/可选🟢
- ✅ 详见：[后端更新协议](../deployment/BACKEND_UPDATE_PROTOCOL.md)

---

### 1. 环境准备

- 安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
- 注册微信小程序账号，获取 AppID

### 2. 导入项目

1. 打开微信开发者工具
2. 选择"导入项目"
3. 选择项目目录
4. 填入 AppID（或使用测试号）
5. 点击"导入"

### 3. 运行项目

- 点击"编译"按钮即可在模拟器中预览
- 使用真机调试可以体验录音功能

### 4. 后端服务

详见 `backend/README.md` 和相关部署文档

**快速启动：**
```bash
cd backend
source venv/bin/activate     # 激活虚拟环境
pip install -r requirements.txt  # 安装依赖
python main.py               # 启动服务（默认 http://127.0.0.1:8000）
```

**配置说明：**
- 修改 `miniprogram/utils/config.js` 中的 `API_BASE_URL`
- 模拟器测试：`http://localhost:8000`
- 真机测试：`http://<你的IP>:8000`
- 生产环境：`https://cshine.xuyucloud.com`

**登录配置：**
- 查看 `docs/deployment/LOGIN.md` 了解完整登录流程
- 配置微信小程序 AppID 和 AppSecret
- 小程序启动时自动完成静默登录

**AI 模型配置：** ✨ 新增
1. 启动后端服务
2. 访问 Web 管理后台：`http://127.0.0.1:8000/static/admin/login.html`
3. 使用默认账号登录（admin / admin123456）
4. 添加 AI 模型配置（OpenAI、Anthropic、豆包、通义等）
5. 小程序端即可选择使用不同的 AI 模型

详见：`docs/features/DEPLOY_AI_MODELS_SYSTEM_20251113.md`

### 5. 当前状态

✅ **已完成功能**

**用户认证** ✨ 新增
- **自动登录**：小程序启动时自动静默登录
- **完整授权**：支持获取用户昵称和头像
- **Token 管理**：JWT Token 自动携带和失效处理
- **状态管理**：全局登录状态管理

**闪记功能**
- **前端页面**：首页、详情页、编辑页
- **核心组件**：导航栏、录音按钮、闪记卡片
- **录音功能**：长按录音、波形动画、上滑取消
- **列表功能**：分类筛选、下拉刷新、收藏管理
- **详情功能**：音频播放、内容查看、操作菜单
- **编辑功能**：修改标题、内容、分类

**会议纪要功能**
- **前端页面**：会议列表、上传页、详情页
- **文件上传**：支持选择音频文件上传
- **状态跟踪**：实时显示处理进度
- **结构化展示**：摘要、要点、行动项、全文分 Tab 展示
- **音频播放**：支持播放会议音频
- **操作功能**：删除、分享（开发中）

**后端服务**
- **认证系统**：微信登录、JWT Token ✅
- **管理员系统**：独立的管理员认证和权限管理 ✅
- **闪记 API**：完整的 CRUD 接口 ✅
- **会议纪要 API**：创建、查询、更新、删除、重新处理 ✅
- **知识库 API**：文件夹 CRUD、会议分类管理 ✅
- **AI 模型管理**：多模型配置、测试、切换 ✅
- **提示词管理**：自定义场景化提示词模板 ✅
- **AI 集成**：语音转写、智能摘要、关键词提取、LLM 分类 ✅
- **会议 AI**：要点提取、行动项识别、说话人分离、多种摘要 ✅
- **云服务**：阿里云 OSS 存储、通义听悟 ASR ✅
- **Web 管理后台**：可视化配置界面 ✅
- **线上部署**：已部署到生产环境 ✅

⏳ **待开发功能**
- 搜索功能（全文搜索、语义搜索）
- 数据导出（导出为 Markdown/PDF）
- 个人中心完善（用户设置、统计数据）
- 标签系统（自定义标签）
- 分享功能（分享到微信好友）
- 会议纪要导出与分享
- 提示词模板的 Web 管理界面（目前只读）
- AI 对话功能（基于会议内容的 Q&A）

## 📸 界面预览

### 首页
- **欢迎区域**：品牌 Slogan 展示
- **录音按钮**：核心交互，支持长按录音、上滑取消
- **统计信息**：显示今日记录数量
- **筛选器**：按分类快速筛选内容
- **闪记列表**：展示历史记录，支持收藏和查看详情

### 录音交互
- 长按录音按钮开始录音
- 松开自动保存
- 上滑超过 60px 进入取消状态
- 实时显示录音时长
- 波形动画反馈

## 🎯 开发计划

按照 PRD-完善版.md 的规划：

### Phase 1：MVP 开发 ✅ **已完成**
- [x] Week 1-2：需求梳理、技术调研、前端框架搭建
- [x] Week 2-3：小程序前端核心页面开发
- [x] Week 3-4：后端接口开发
- [x] Week 4-5：AI 服务集成（阿里云通义听悟）
- [x] Week 5：联调测试
- [x] Week 6：真机测试 + Bug 修复

### Phase 2：功能完善 ✅ **已完成**
- [x] 会议纪要功能 ✅
- [x] 智能分类（规则 + LLM 双模式）✅
- [x] 知识库文件夹管理 ✅
- [x] AI 模型管理系统 ✅
- [x] Web 管理后台 ✅
- [x] 用户体验优化（波形播放器、模态框、操作菜单）✅
- [ ] 搜索功能
- [ ] 数据导出

**🎉 当前进度：Phase 2 核心功能已完成，AI 系统全面升级！**

### Phase 3：上线运营 🚀 **进行中**
- [x] 申请微信小程序账号 ✅
- [x] 配置生产环境（域名、HTTPS、服务器）✅
- [x] 后端服务部署 ✅
- [ ] 小程序审核
- [ ] 灰度发布
- [ ] 正式上线

**当前环境**：
- **生产后端**：https://cshine.xuyucloud.com
- **管理后台**：https://cshine.xuyucloud.com/static/admin/login.html
- **数据库**：PostgreSQL（生产）
- **部署方式**：Systemd 服务 + Nginx 反向代理

## 🎨 设计规范

详见 `PRD-完善版.md` 第 12.1 节

### 色彩系统
- **主色**：#4A6FE8（天蓝色）
- **辅色**：#7B61FF（宇宙紫）
- **渐变**：135deg, #4A6FE8 → #7B61FF

### 字体规范
- **标题**：HarmonyOS Sans Bold
- **正文**：PingFang SC Regular
- **字号**：12-32px 响应式字号

### 间距规范
- **基础单位**：8rpx（4px）
- **常用间距**：16rpx、24rpx、32rpx
- **页面边距**：32rpx（16px）

## 🔧 开发规范

### 命名规范
- **文件名**：kebab-case（如 `record-button.js`）
- **组件名**：PascalCase（如 `RecordButton`）
- **变量名**：camelCase（如 `flashList`）
- **样式类**：kebab-case（如 `.flash-card`）

### 注释规范
```javascript
/**
 * 函数说明
 * @param {string} param - 参数说明
 * @returns {boolean} 返回值说明
 */
function example(param) {
  // 实现逻辑
}
```

### Git 提交规范
```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

## 📞 API 接口说明

详见 `backend/README.md` 和 `PRD-完善版.md` 第 7 章

### 核心接口（已实现）

**认证接口**
- `POST /api/v1/auth/login` - 微信登录 ✅
- `GET /api/v1/auth/me` - 获取当前用户信息 ✅

**管理员接口** ✨ 新增
- `POST /api/v1/admin/login` - 管理员登录 ✅
- `GET /api/v1/admin/me` - 获取管理员信息 ✅

**闪记接口**
- `POST /api/v1/flash/create` - 创建闪记（支持指定 AI 模型）✅
- `GET /api/v1/flash/list` - 获取闪记列表 ✅
- `GET /api/v1/flash/{id}` - 获取闪记详情 ✅
- `PUT /api/v1/flash/{id}` - 更新闪记 ✅
- `DELETE /api/v1/flash/{id}` - 删除闪记 ✅
- `PUT /api/v1/flash/{id}/favorite` - 收藏/取消收藏 ✅
- `GET /api/v1/flash/{id}/ai-status` - 查询 AI 处理状态 ✅

**会议纪要接口**
- `POST /api/v1/meeting/create` - 创建会议纪要（支持指定 AI 模型）✅
- `GET /api/v1/meeting/list` - 获取会议列表 ✅
- `GET /api/v1/meeting/{id}` - 获取会议详情 ✅
- `PUT /api/v1/meeting/{id}` - 更新会议纪要 ✅
- `DELETE /api/v1/meeting/{id}` - 删除会议纪要 ✅
- `POST /api/v1/meeting/{id}/reprocess` - 重新处理会议 ✅
- `GET /api/v1/meeting/{id}/status` - 查询处理状态 ✅

**知识库接口** ✨ 新增
- `POST /api/v1/folders` - 创建文件夹 ✅
- `GET /api/v1/folders` - 获取文件夹列表 ✅
- `PUT /api/v1/folders/{id}` - 更新文件夹 ✅
- `DELETE /api/v1/folders/{id}` - 删除文件夹 ✅

**AI 模型管理接口** ✨ 新增
- `GET /api/v1/ai-models/available` - 获取可用模型列表（用户端）✅
- `POST /api/v1/admin/ai-models` - 创建 AI 模型（管理员）✅
- `GET /api/v1/admin/ai-models` - 获取模型列表（管理员）✅
- `PUT /api/v1/admin/ai-models/{id}` - 更新模型配置（管理员）✅
- `DELETE /api/v1/admin/ai-models/{id}` - 删除模型（管理员）✅
- `POST /api/v1/admin/ai-models/{id}/test` - 测试模型连接（管理员）✅

**提示词管理接口** ✨ 新增
- `GET /api/v1/admin/prompts` - 获取提示词列表（管理员）✅
- `POST /api/v1/admin/prompts` - 创建提示词（管理员）✅
- `PUT /api/v1/admin/prompts/{id}` - 更新提示词（管理员）✅
- `DELETE /api/v1/admin/prompts/{id}` - 删除提示词（管理员）✅

**文件上传接口**
- `POST /api/v1/upload/audio` - 上传音频文件 ✅

**健康检查**
- `GET /health` - 服务健康检查 ✅

## 🤝 贡献指南

欢迎贡献代码、提出建议！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目仅供学习交流使用。

## 📮 联系方式

如有问题或建议，欢迎联系：
- 项目主页：[GitHub - Cshine](https://github.com/cosmosva/Cshine)
- Issues：[提交问题或建议](https://github.com/cosmosva/Cshine/issues)
- 邮箱：cosmosva@example.com

## 🔖 版本历史

查看 [docs/core/CHANGELOG.md](docs/core/CHANGELOG.md) 了解详细的版本更新记录。

### v0.9.1 (2025-11-13) - 当前版本

**🎉 AI 模型管理系统完整发布！**

核心更新：
- ✅ 多 AI 模型支持（OpenAI、Anthropic、豆包、通义）
- ✅ Web 管理后台（可视化配置）
- ✅ 小程序端 AI 模型选择
- ✅ LLM 智能分类器
- ✅ 管理员认证系统
- ✅ 提示词模板管理
- ✅ 自动降级机制

### v0.6.0 (2025-11-13)

**🔧 AI 模型统一管理系统**

核心功能：
- ✅ 数据库新增 AI 模型配置表
- ✅ LLM 抽象层设计
- ✅ 多模型工厂模式
- ✅ 闪记和会议支持 AI 模型选择

### v0.5.0 (2025-11-10)

**📚 知识库管理增强**

核心功能：
- ✅ 知识库文件夹 CRUD
- ✅ 会议分类管理
- ✅ 会议复制和移动
- ✅ 会议重新处理
- ✅ 波形播放器组件

### v0.4.0 (2025-11-08)

**🎙️ 会议纪要功能**

核心功能：
- ✅ 会议音频上传
- ✅ 智能转写和摘要
- ✅ 说话人分离
- ✅ 章节划分
- ✅ 要点和行动项提取

### v0.1.0 (2025-11-07)

**🎉 首个 MVP 版本发布！**

核心功能：
- ✅ 语音录制与播放
- ✅ AI 智能转写（阿里云通义听悟）
- ✅ 智能摘要和关键词提取
- ✅ 自动分类（工作/生活/学习/灵感/其他）
- ✅ 闪记列表展示与筛选
- ✅ 收藏功能
- ✅ 编辑与删除
- ✅ 详情页面
- ✅ 响应式设计与安全区域适配

---

**Made with ❤️ by Cshine Team**

*让每个想法都发光 ✨*

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star 支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=cosmosva/Cshine&type=Date)](https://star-history.com/#cosmosva/Cshine&Date)

