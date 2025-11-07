# Cshine 微信小程序

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/cosmosva/Cshine)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![WeChat](https://img.shields.io/badge/WeChat-MiniProgram-07C160.svg)](https://mp.weixin.qq.com/)

> **Let Your Ideas Shine. ✨**
> AI 驱动的语音记录与灵感管理工具
>
> **当前版本**: v0.1.0 | **发布日期**: 2025-11-07

## 📱 项目简介

Cshine 是一款基于微信小程序的智能语音记录工具，帮助用户随时随地捕捉灵感、记录想法。通过 AI 技术自动将语音转为文字并生成智能摘要，让每个想法都能被轻松管理和回顾。

### 核心功能

- 🎙️ **闪记（Voice Flash）**：长按录音，即刻记录灵感 ✅
- 📝 **智能转写**：自动将语音转为文字（阿里云通义听悟）✅
- 🧠 **AI 摘要**：自动生成内容摘要和关键词 ✅
- 🏷️ **智能分类**：自动识别内容类别（工作/生活/学习/灵感/其他）✅
- 🔍 **快速检索**：按分类筛选历史记录 ✅
- ⭐ **收藏管理**：标记重要内容，快速访问 ✅
- 📖 **详情查看**：查看完整内容、播放音频 ✅
- ✏️ **编辑功能**：修改标题、内容和分类 ✅
- 🗑️ **删除功能**：删除不需要的记录 ✅

## 🎨 设计特色

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
- **智能分类**：基于关键词的规则分类器
- **异步处理**：Python Threading

## 📁 项目结构

```
Cshine/
├── app.js                  # 小程序入口
├── app.json                # 全局配置
├── app.wxss                # 全局样式
├── components/             # 组件目录
│   ├── navigation-bar/     # 导航栏组件
│   ├── record-button/      # 录音按钮组件（支持长按、波形动画）
│   └── flash-card/         # 闪记卡片组件
├── pages/                  # 页面目录
│   ├── index/              # 首页（列表、录音、筛选）
│   ├── detail/             # 详情页（查看、播放、操作）
│   └── edit/               # 编辑页（修改内容）
├── styles/                 # 样式系统
│   ├── variables.wxss      # 全局变量（色彩、尺寸等）
│   └── common.wxss         # 通用样式（工具类）
├── utils/                  # 工具类
│   ├── api.js              # API 接口封装
│   ├── request.js          # 网络请求封装
│   ├── config.js           # 配置文件
│   ├── format.js           # 格式化工具
│   ├── storage.js          # 本地存储
│   └── toast.js            # 提示工具
├── backend/                # 后端服务
│   ├── app/                # 应用目录
│   │   ├── api/            # API 路由
│   │   ├── models.py       # 数据模型
│   │   ├── schemas.py      # 数据验证
│   │   ├── database.py     # 数据库连接
│   │   ├── dependencies.py # 依赖注入
│   │   ├── services/       # 业务服务
│   │   │   ├── tingwu_service.py    # 通义听悟服务
│   │   │   ├── classifier.py        # 智能分类器
│   │   │   └── ai_processor.py      # AI 处理器
│   │   └── utils/          # 工具函数
│   ├── main.py             # 入口文件
│   ├── config.py           # 配置管理
│   ├── requirements.txt    # 依赖列表
│   └── README.md           # 后端文档
├── PRD-完善版.md            # 产品需求文档
└── README.md               # 项目说明（本文件）
```

## 🚀 快速开始

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

详见 `backend/README.md` 和 `backend/快速开始.md`

**快速启动：**
```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
python main.py             # 启动服务
```

**配置说明：**
- 修改 `utils/config.js` 中的 `API_BASE_URL`
- 模拟器测试：`http://localhost:8000`
- 真机测试：`http://<你的IP>:8000`

### 5. 当前状态

✅ **已完成功能**
- **前端页面**：首页、详情页、编辑页
- **核心组件**：导航栏、录音按钮、闪记卡片
- **录音功能**：长按录音、波形动画、上滑取消
- **列表功能**：分类筛选、下拉刷新、收藏管理
- **详情功能**：音频播放、内容查看、操作菜单
- **编辑功能**：修改标题、内容、分类
- **后端 API**：完整的 CRUD 接口
- **AI 集成**：语音转写、智能摘要、关键词提取、自动分类
- **云服务**：阿里云 OSS 存储、通义听悟 ASR
- **真机测试**：通过 ✅

⏳ **待开发功能**
- 会议纪要模式（长时间录音）
- 搜索功能（全文搜索）
- 数据导出（导出为 Markdown/PDF）
- 个人中心（用户设置、统计数据）
- 标签系统（自定义标签）
- 分享功能（分享到微信好友）

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

**🎉 当前进度：Phase 1 已完成，核心功能全部实现！**

### Phase 2：功能完善（待开发）
- [ ] 会议纪要功能
- [x] 智能分类（已完成基础版）
- [ ] 搜索功能
- [ ] 用户体验优化（骨架屏、更好的加载动画）
- [ ] 数据导出

### Phase 3：上线运营（待规划）
- [ ] 申请微信小程序账号
- [ ] 配置生产环境（域名、HTTPS、服务器）
- [ ] 小程序审核
- [ ] 灰度发布
- [ ] 正式上线

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
- `POST /api/v1/auth/login` - 微信登录
- `GET /api/v1/auth/me` - 获取当前用户信息

**闪记接口**
- `POST /api/v1/flash/create` - 创建闪记 ✅
- `GET /api/v1/flash/list` - 获取闪记列表 ✅
- `GET /api/v1/flash/{id}` - 获取闪记详情 ✅
- `PUT /api/v1/flash/{id}` - 更新闪记 ✅
- `DELETE /api/v1/flash/{id}` - 删除闪记 ✅
- `PUT /api/v1/flash/{id}/favorite` - 收藏/取消收藏 ✅
- `GET /api/v1/flash/{id}/ai-status` - 查询 AI 处理状态 ✅

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

查看 [CHANGELOG.md](CHANGELOG.md) 了解详细的版本更新记录。

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

技术亮点：
- 统一的 CSS 变量设计系统
- scroll-view 滚动优化
- 固定定位按钮与安全区域处理
- 录音波形动画
- 完整的 FastAPI 后端

---

**Made with ❤️ by Cshine Team**

*让每个想法都发光 ✨*

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star 支持一下！

[![Star History Chart](https://api.star-history.com/svg?repos=cosmosva/Cshine&type=Date)](https://star-history.com/#cosmosva/Cshine&Date)

