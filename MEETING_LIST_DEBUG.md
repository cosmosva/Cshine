# 会议列表页面调试指南

## 🐛 问题：页面只显示数字"2"和"1"

### 可能的原因

1. **微信开发者工具缓存**
2. **数据没有正确加载**
3. **页面没有重新编译**

## ✅ 解决步骤

### 步骤1：清理缓存并重新编译

在微信开发者工具中：

1. **清理缓存**
   - 点击菜单：`工具` → `清除缓存`
   - 选择：`清除全部缓存`

2. **重新编译**
   - 点击菜单：`编译` → `重新构建 npm`（如果有用到npm）
   - 点击 `编译` 按钮（或按 Ctrl/Cmd + B）

3. **重启模拟器**
   - 关闭模拟器
   - 重新打开

### 步骤2：检查数据加载

打开控制台（Console），查看：

1. **是否有API请求**
   ```
   应该看到：会议列表（已解包）: {...}
   ```

2. **检查meetingList数据**
   - 在Console中输入：`getCurrentPages()[getCurrentPages().length-1].data.meetingList`
   - 应该显示会议数组

3. **检查错误信息**
   - 查看是否有红色错误信息
   - 特别注意API请求失败的错误

### 步骤3：手动触发数据加载

如果数据没有加载，在Console中执行：

```javascript
const page = getCurrentPages()[getCurrentPages().length-1];
page.loadMeetingList(true);
```

### 步骤4：检查页面路径

确认当前页面路径：

在Console中执行：
```javascript
getCurrentPages()[getCurrentPages().length-1].route
```

应该显示：`pages/meeting/list`

### 步骤5：验证文件更新

检查文件时间戳：

```bash
ls -la pages/meeting/list.*
```

确认文件是最新修改的。

## 🔍 调试检查清单

### 文件检查
- [ ] `pages/meeting/list.wxml` - 132行
- [ ] `pages/meeting/list.wxss` - 包含 .card-row-1, .card-row-2, .card-row-3
- [ ] `pages/meeting/list.js` - 包含 loadMeetingList 函数
- [ ] `pages/meeting/list.json` - 配置正确

### 后端检查
- [ ] 后端服务运行正常
- [ ] API端点可访问：`http://localhost:8000/health`
- [ ] 会议列表API返回数据

### 数据检查
在Console中执行以下命令并检查结果：

```javascript
// 1. 检查当前页面
getCurrentPages()[getCurrentPages().length-1].route

// 2. 检查页面数据
const page = getCurrentPages()[getCurrentPages().length-1];
console.log('meetingList:', page.data.meetingList);
console.log('loading:', page.data.loading);
console.log('total:', page.data.total);

// 3. 手动加载数据
page.loadMeetingList(true);
```

## 💡 常见问题

### Q1: 页面显示"暂无会议纪要"
**A**: 这是正常的，说明数据库中没有会议记录。请先上传会议音频。

### Q2: 页面一直显示加载状态
**A**: 可能是后端服务未启动或API请求超时。
解决方法：
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Q3: 只显示数字"2"和"1"
**A**: 这通常是缓存问题。
解决方法：
1. 清理缓存
2. 重新编译
3. 重启开发者工具

### Q4: 点击卡片没有反应
**A**: 检查Console是否有JavaScript错误。

## 📱 预期效果

正确的页面应该显示：

```
┌─────────────────────────────────────────┐
│ ☰ 录音文件                  媒体    ⇅  │
├─────────────────────────────────────────┤
│ Day7 01短视频创作全流程...  ☆  1h 20m  │
│ 2025-09-17 13:09:39         [处理中]   │
│ 🔊 脚本设计  脚本设计  人设定位         │
├─────────────────────────────────────────┤
│ Day6 03故事的高阶手法...    ⭐ 1h 17m  │
│ 2025-09-16 16:32:26                    │
│ 🔊 脚本设计  纪实片  媒体责任           │
└─────────────────────────────────────────┘
```

## 🛠 强制刷新方法

如果以上方法都不行，尝试：

1. **完全关闭微信开发者工具**
2. **删除工具缓存**（位置因系统而异）
3. **重新打开项目**
4. **等待完全加载后再查看**

## 📞 需要帮助？

如果问题仍然存在，请提供：
1. Console中的错误信息截图
2. Network标签中的API请求情况
3. 页面data的完整内容（通过上面的调试命令获取）

