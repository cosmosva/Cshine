# Cshine 小程序端

> **Let Your Ideas Shine. ✨**

这是 Cshine 的微信小程序代码目录。

## 📱 使用微信开发者工具打开

1. 打开微信开发者工具
2. 选择"导入项目"
3. **选择当前目录**（`/miniprogram`）作为项目目录
4. 填入 AppID（或使用测试号）
5. 点击"导入"

## 📁 目录结构

```
miniprogram/
├── app.js                  # 小程序入口
├── app.json                # 全局配置
├── app.wxss                # 全局样式
├── components/             # 组件目录
│   ├── navigation-bar/     # 导航栏组件
│   ├── record-button/      # 录音按钮组件
│   ├── flash-card/         # 闪记卡片组件
│   └── ...
├── pages/                  # 页面目录
│   ├── index/              # Cshine 主页（闪记）
│   ├── meeting/            # 会议纪要
│   ├── profile/            # 个人中心
│   └── ...
├── utils/                  # 工具类
│   ├── api.js              # API 接口封装
│   ├── request.js          # 网络请求
│   ├── config.js           # 配置文件
│   └── ...
├── assets/                 # 资源文件
│   ├── icons/              # 图标
│   └── images/             # 图片
├── styles/                 # 样式系统
│   ├── variables.wxss      # 全局变量
│   └── common.wxss         # 通用样式
└── project.config.json     # 小程序项目配置
```

## ⚙️ 配置说明

### 后端 API 地址

修改 `utils/config.js` 中的 `API_BASE_URL`：

```javascript
// 开发环境（模拟器）
development: 'http://localhost:8000'

// 真机测试
development: 'http://your-local-ip:8000'

// 生产环境
production: 'https://cshine.xuyucloud.com'
```

### AppID 配置

在 `project.config.json` 中配置你的 AppID：

```json
{
  "appid": "your_appid_here"
}
```

## 🚀 开发指南

### 运行项目

1. 确保后端服务已启动（参考 `../backend/README.md`）
2. 在微信开发者工具中点击"编译"
3. 在模拟器或真机中预览

### 真机调试

1. 点击工具栏的"预览"按钮
2. 使用微信扫描二维码
3. 在真机上测试（录音功能仅真机可用）

## 📖 更多文档

- [项目整体说明](../README.md)
- [后端文档](../backend/README.md)
- [开发规范](../docs/core/DEVELOPMENT_GUIDE.md)
- [产品需求文档](../docs/core/PRD-完善版.md)

## 🎯 核心功能

### 闪记（Cshine）
- 🎙️ 长按录音，快速记录灵感
- 📝 AI 智能转写和摘要
- 🏷️ 自动分类管理

### 会议纪要（Knowledge）
- 📋 上传会议音频
- 👥 说话人分离
- 💡 智能提取要点和行动项
- 📑 章节划分和摘要

### 个人中心（Profile）
- 👤 用户信息管理
- 📊 数据统计
- ⚙️ 设置和帮助

## 🎨 开发规范

- 遵循微信小程序开发规范
- 使用 CSS Variables 管理样式
- 组件化开发
- 代码注释清晰

## ⚠️ 注意事项

- 录音功能需要在真机上测试
- 开发环境需要配置合法域名（可在开发者工具中跳过）
- 生产环境必须使用 HTTPS

---

**版本**: v0.5.18  
**更新日期**: 2025-11-13

**Let Your Ideas Shine. ✨**

