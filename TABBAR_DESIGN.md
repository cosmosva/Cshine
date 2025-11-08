# TabBar 底部导航设计

## 📱 设计概览

Cshine 采用经典的三 Tab 底部导航设计，提供清晰的功能分区和便捷的页面切换。

## 🎯 三大功能模块

### 1. 知识库（会议记录）
- **图标**: 📚 书本/文档
- **页面**: `pages/meeting/list`
- **功能**: 
  - 会议纪要列表
  - 状态筛选
  - 快速查看会议详情
  - 上传新的会议音频

### 2. Cshine（闪记）
- **图标**: ⚡ 闪电
- **页面**: `pages/index/index`  
- **功能**:
  - 快速语音录制
  - 闪记列表
  - 分类筛选
  - 收藏管理

### 3. 我的（个人中心）
- **图标**: 👤 用户头像
- **页面**: `pages/profile/profile`
- **功能**:
  - 用户信息展示
  - 数据统计
  - 设置和帮助
  - 数据导出

## 🎨 设计规范

### 颜色
- **未选中**: #999999（灰色）
- **选中**: #4A6FE8（品牌蓝）
- **背景**: #FFFFFF（白色）

### 图标
- **尺寸**: 81x81 像素
- **格式**: PNG
- **风格**: 简洁、统一、易识别

## 📂 文件结构

```
Cshine/
├── app.json                      # TabBar 配置
├── assets/
│   └── icons/                    # TabBar 图标
│       ├── knowledge.png         # 知识库-普通
│       ├── knowledge-active.png  # 知识库-选中
│       ├── flash.png             # Cshine-普通
│       ├── flash-active.png      # Cshine-选中
│       ├── profile.png           # 我的-普通
│       ├── profile-active.png    # 我的-选中
│       ├── README.md             # 图标说明
│       ├── QUICK_START.md        # 快速获取指南
│       └── generate-icons.md     # 生成方法
└── pages/
    ├── index/                    # Cshine 主页
    ├── meeting/
    │   └── list/                 # 知识库页面
    └── profile/                  # 我的页面
```

## 🔧 技术实现

### app.json 配置

```json
{
  "tabBar": {
    "color": "#999999",
    "selectedColor": "#4A6FE8",
    "backgroundColor": "#ffffff",
    "borderStyle": "black",
    "list": [
      {
        "pagePath": "pages/meeting/list",
        "text": "知识库",
        "iconPath": "assets/icons/knowledge.png",
        "selectedIconPath": "assets/icons/knowledge-active.png"
      },
      {
        "pagePath": "pages/index/index",
        "text": "Cshine",
        "iconPath": "assets/icons/flash.png",
        "selectedIconPath": "assets/icons/flash-active.png"
      },
      {
        "pagePath": "pages/profile/profile",
        "text": "我的",
        "iconPath": "assets/icons/profile.png",
        "selectedIconPath": "assets/icons/profile-active.png"
      }
    ]
  }
}
```

### 页面跳转

**跳转到 TabBar 页面**（使用 `wx.switchTab`）：
```javascript
// ✅ 正确
wx.switchTab({
  url: '/pages/meeting/list'
})

// ❌ 错误（TabBar 页面不能用 navigateTo）
wx.navigateTo({
  url: '/pages/meeting/list'
})
```

**跳转到非 TabBar 页面**（使用 `wx.navigateTo`）：
```javascript
wx.navigateTo({
  url: '/pages/meeting/detail?id=xxx'
})
```

## 📊 用户体验优化

### 1. 清晰的功能分区
- **知识库**: 长时间记录，沉淀知识
- **Cshine**: 快速记录，即时灵感
- **我的**: 个人中心，数据管理

### 2. 便捷的切换
- 一键切换功能模块
- 保持各页面状态
- 无需频繁返回

### 3. 视觉反馈
- 选中态明显区分
- 品牌色突出显示
- 图标清晰易识别

## 🚀 快速开始

### 第一步：准备图标

查看 `assets/icons/QUICK_START.md`，选择以下任一方式：

1. **IconFont**（推荐）- 3分钟
2. **Figma** - 5分钟  
3. **占位图标** - 1分钟

### 第二步：放置图标

将6个图标文件放到 `assets/icons/` 目录

### 第三步：运行项目

```bash
# 打开微信开发者工具
# 导入项目
# 查看 TabBar 效果
```

## ✨ 功能特性

### 1. 知识库页面

**数据统计**
- 总会议数量
- 处理中/已完成/失败数量
- 快速筛选和查看

**快速操作**
- 上传新会议
- 查看会议详情
- 删除会议记录

### 2. Cshine 页面

**语音录制**
- 长按录音
- 实时波形
- 智能转写

**闪记管理**
- 分类筛选
- 收藏管理
- 快速编辑

### 3. 我的页面

**用户信息**
- 头像昵称
- 用户ID
- 登录/退出

**数据统计**
- 闪记数量
- 会议纪要
- 今日新增
- 总时长

**功能菜单**
- ⚙️ 设置
- 📤 数据导出
- 🗑️ 清除缓存
- ❓ 帮助中心
- ℹ️ 关于 Cshine

## 📱 适配说明

### iPhone X 及以上
- 自动适配底部安全区域
- TabBar 高度自动调整
- 内容区域避开安全区

### 小屏幕设备
- 图标自适应缩放
- 文字清晰可读
- 触控区域足够大

## 🎯 设计原则

1. **简洁优先**: 三个 Tab 足够，不过度复杂
2. **功能明确**: 每个 Tab 职责清晰
3. **易于使用**: 符合用户习惯
4. **视觉统一**: 与品牌色系一致
5. **响应及时**: 切换流畅无延迟

## 🔄 未来规划

### Phase 1（当前）
- [x] 基础三 Tab 结构
- [x] 核心页面实现
- [x] 图标规范制定

### Phase 2（规划中）
- [ ] 个性化主题
- [ ] 自定义 Tab 顺序
- [ ] 角标提醒（未读/新增）
- [ ] 更多设置选项

### Phase 3（长期）
- [ ] 手势操作（侧滑切换）
- [ ] 快捷操作（长按 Tab）
- [ ] 动态图标
- [ ] 个性化配置

## 📚 相关文档

- `assets/icons/README.md` - 图标详细说明
- `assets/icons/QUICK_START.md` - 快速获取图标指南
- `assets/icons/generate-icons.md` - 生成方法详解
- `README.md` - 项目总体介绍
- `CHANGELOG.md` - 版本更新记录

## ⚠️ 注意事项

1. **图标必须是本地文件**，不能使用网络图片
2. **TabBar 页面必须在 pages 数组前面**
3. **切换 TabBar 使用 `wx.switchTab`**
4. **图标尺寸必须是 81x81 px**
5. **至少2个，最多5个 Tab**
6. **TabBar 页面不能携带参数**

## 🎨 设计资源

### 图标库
- [IconFont](https://www.iconfont.cn/) - 免费中文图标库
- [Flaticon](https://www.flaticon.com/) - 国际图标库
- [Icons8](https://icons8.com/) - 图标编辑器

### 设计工具
- [Figma](https://www.figma.com/) - 在线设计工具
- [Canva](https://www.canva.com/) - 快速生成工具
- [Iconify](https://iconify.design/) - 图标插件

### 颜色工具
- [Coolors](https://coolors.co/) - 配色生成器
- [Adobe Color](https://color.adobe.com/) - 专业配色
- [ColorHunt](https://colorhunt.co/) - 配色灵感

---

**版本**: v0.2.1 (2025-11-07)  
**作者**: Cosmos  
**更新**: TabBar 导航系统设计文档

