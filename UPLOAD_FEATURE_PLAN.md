# "+" 按钮功能开发计划

## 1. 核心功能流程

### 1.1 上传文件流程

```
点击 "+" 按钮（二级导航栏右侧）
    ↓
ActionSheet 弹出（上传文件 / 新建知识库）
    ↓
选择 "上传文件"
    ↓
wx.chooseMessageFile() 文件选择器
    - 支持格式：mp3, m4a, wav
    - 文件大小限制：< 500MB
    ↓
知识库选择页面（Modal）
    - 标题："选择知识库"
    - 显示当前知识库（默认："录音文件"）
    - 显示所有知识库列表（来自 data.folders）
    - "新建知识库" 按钮
    - "确认" 按钮
    ↓
提取音频时长
    - wx.createInnerAudioContext()
    - onCanplay 事件获取 duration
    ↓
跳转到上传进度页面（pages/meeting/upload）
    - 显示文件名
    - 显示上传时间（当前时间）
    - 显示音频时长
    - 显示文件格式
    - 上传进度条（wx.uploadFile + onProgressUpdate）
    - 状态文案："上传中" / "正在上传文件到云端"
    ↓
OSS 上传完成
    ↓
调用后端 API 创建会议记录
    - 携带 folder_id（选中的知识库ID）
    ↓
触发 AI 处理（后台异步）
    ↓
返回列表页并刷新
```

### 1.2 新建知识库流程

```
点击 "+" 按钮
    ↓
ActionSheet 弹出
    ↓
选择 "新建知识库"
    ↓
Modal 输入框弹出
    - 标题："新建知识库"
    - 输入框：placeholder="请输入知识库名称"
    - 按钮：取消 / 确认
    ↓
输入知识库名称
    ↓
点击 "确认"
    ↓
调用后端 API 创建文件夹
    - POST /api/v1/folders
    - Body: { name: "xxx" }
    ↓
更新本地 data.folders 列表
    ↓
Toast 提示："知识库创建成功"
    ↓
关闭 Modal
```

### 1.3 知识库联动逻辑

```
状态管理：
- currentFolderId: null（null = "录音文件"，即全部）
- currentFolderName: "录音文件"

抽屉选择文件夹 →
    更新 currentFolderId 和 currentFolderName →
    更新二级导航栏标题 →
    重新加载会议列表（筛选 folder_id）

上传文件 →
    默认使用 currentFolderId →
    知识库选择页可切换 →
    创建会议时携带 folder_id
```

## 2. 技术实现要点

### 2.1 微信 API 调用

**文件选择**
```javascript
wx.chooseMessageFile({
  count: 1,
  type: 'file',
  extension: ['mp3', 'm4a', 'wav'],
  success: (res) => {
    const tempFilePath = res.tempFiles[0].path
    const fileName = res.tempFiles[0].name
    const fileSize = res.tempFiles[0].size
    // 继续处理...
  }
})
```

**音频时长提取**
```javascript
const audio = wx.createInnerAudioContext()
audio.src = tempFilePath
audio.onCanplay(() => {
  const duration = Math.floor(audio.duration)
  audio.destroy()
  // 获取到时长后继续...
})
```

**OSS 上传（带进度）**
```javascript
const uploadTask = wx.uploadFile({
  url: ossUploadUrl,
  filePath: tempFilePath,
  name: 'file',
  formData: { /* OSS 签名参数 */ },
  success: (res) => {
    // 上传成功
  }
})

uploadTask.onProgressUpdate((res) => {
  const progress = res.progress
  this.setData({ uploadProgress: progress })
})
```

### 2.2 状态管理

```javascript
// pages/meeting/list.js
data: {
  // 知识库状态
  currentFolderId: null,        // 当前选中的知识库ID
  currentFolderName: '录音文件', // 当前知识库名称

  // UI 状态
  showUploadSheet: false,       // 上传/新建 ActionSheet
  showFolderSelector: false,    // 知识库选择 Modal
  showCreateFolder: false,      // 新建知识库 Modal

  // 临时数据
  tempSelectedFile: null,       // 临时存储选中的文件信息
  newFolderName: '',            // 新建知识库名称输入

  // 现有数据
  folders: [...],               // 知识库列表（从后端获取）
  totalCount: 0                 // 总文件数
}
```

### 2.3 后端 API

**创建知识库**
```
POST /api/v1/folders
Body: { name: "知识库名称" }
Response: { id: 1, name: "...", count: 0, created_at: "..." }
```

**获取知识库列表**
```
GET /api/v1/folders
Response: [
  { id: 1, name: "短视频", count: 6 },
  { id: 2, name: "大海", count: 1 },
  ...
]
```

**创建会议记录（带 folder_id）**
```
POST /api/v1/meeting/create
Body: {
  title: "会议标题",
  audio_url: "oss://...",
  audio_duration: 120,
  folder_id: 1  // 关键：指定知识库
}
```

**获取会议列表（按 folder_id 筛选）**
```
GET /api/v1/meeting/list?folder_id=1
Response: { items: [...], total: 10 }
```

## 3. UI 组件设计

### 3.1 上传 ActionSheet（list.wxml）

```xml
<!-- 上传操作选择 -->
<view class="action-sheet-mask" wx:if="{{showUploadSheet}}" bindtap="hideUploadSheet"></view>
<view class="action-sheet {{showUploadSheet ? 'show' : ''}}">
  <view class="action-sheet-header">
    <text class="action-sheet-title">选择操作</text>
    <view class="action-sheet-close" bindtap="hideUploadSheet">✕</view>
  </view>
  <view class="action-sheet-body">
    <view class="action-item" bindtap="handleUploadFile">
      <text class="action-icon">📁</text>
      <text class="action-label">上传文件</text>
    </view>
    <view class="action-item" bindtap="handleCreateFolder">
      <text class="action-icon">➕</text>
      <text class="action-label">新建知识库</text>
    </view>
  </view>
</view>
```

### 3.2 知识库选择 Modal（list.wxml）

```xml
<!-- 知识库选择 -->
<view class="modal-mask" wx:if="{{showFolderSelector}}" bindtap="hideFolderSelector"></view>
<view class="modal {{showFolderSelector ? 'show' : ''}}">
  <view class="modal-header">
    <text class="modal-title">选择知识库</text>
  </view>
  <view class="modal-body">
    <text class="current-folder">当前知识库：{{currentFolderName}}</text>

    <scroll-view class="folder-list" scroll-y>
      <!-- 录音文件（全部） -->
      <view class="folder-option {{currentFolderId === null ? 'selected' : ''}}"
            bindtap="selectFolderForUpload" data-id="{{null}}" data-name="录音文件">
        <text class="folder-name">录音文件</text>
        <text class="check-icon" wx:if="{{currentFolderId === null}}">✓</text>
      </view>

      <!-- 用户创建的知识库 -->
      <view class="folder-option {{currentFolderId === item.id ? 'selected' : ''}}"
            wx:for="{{folders}}" wx:key="id"
            bindtap="selectFolderForUpload" data-id="{{item.id}}" data-name="{{item.name}}">
        <text class="folder-name">{{item.name}}</text>
        <text class="check-icon" wx:if="{{currentFolderId === item.id}}">✓</text>
      </view>
    </scroll-view>

    <view class="modal-actions">
      <view class="btn-secondary" bindtap="handleCreateFolder">新建知识库</view>
      <view class="btn-primary" bindtap="confirmFolderSelection">确认</view>
    </view>
  </view>
</view>
```

### 3.3 新建知识库 Modal（list.wxml）

```xml
<!-- 新建知识库 -->
<view class="modal-mask" wx:if="{{showCreateFolder}}" catchtap="hideCreateFolder"></view>
<view class="modal small {{showCreateFolder ? 'show' : ''}}" catchtap="preventClose">
  <view class="modal-header">
    <text class="modal-title">新建知识库</text>
  </view>
  <view class="modal-body">
    <input class="folder-name-input"
           placeholder="请输入知识库名称"
           value="{{newFolderName}}"
           bindinput="onFolderNameInput"
           maxlength="20" />
  </view>
  <view class="modal-footer">
    <view class="btn-secondary" bindtap="hideCreateFolder">取消</view>
    <view class="btn-primary" bindtap="confirmCreateFolder">确认</view>
  </view>
</view>
```

### 3.4 上传进度页（upload.wxml）

```xml
<!-- 修改现有页面的文案 -->
<view class="upload-page">
  <view class="file-info">
    <text class="file-name">{{fileName}}</text>
    <text class="upload-time">上传时间：{{uploadTime}}</text>
    <text class="audio-duration">音频时长：{{duration}}</text>
    <text class="file-format">格式：{{fileFormat}}</text>
  </view>

  <view class="upload-progress">
    <text class="status-text">上传中</text> <!-- 修改：之前是"下载中" -->
    <progress percent="{{uploadProgress}}" stroke-width="4" activeColor="#4A6FE8" />
    <text class="progress-text">{{uploadProgress}}%</text>
  </view>

  <view class="upload-status">
    <text class="status-desc">正在上传文件到云端</text> <!-- 修改：之前是"正在从云端下载文件" -->
  </view>
</view>
```

## 4. 样式规范（TicNote 风格）

### 4.1 ActionSheet 样式

```css
/* 复用现有的 action-sheet 样式 */
.action-sheet {
  /* 已有样式，无需修改 */
}

.action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
}

.action-icon {
  font-size: 20px;
}
```

### 4.2 Modal 样式

```css
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1001;
  opacity: 0;
  transition: opacity 0.3s;
}

.modal-mask.show {
  opacity: 1;
}

.modal {
  position: fixed;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%) scale(0.8);
  width: 80%;
  max-width: 400px;
  background-color: #FFFFFF;
  border-radius: 16px;
  z-index: 1002;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal.show {
  transform: translate(-50%, -50%) scale(1);
  opacity: 1;
}

.modal-header {
  padding: 20px 16px 16px;
  border-bottom: 0.5px solid #EBEBEB;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #1A1A1A;
}

.modal-body {
  padding: 20px 16px;
  max-height: 400px;
  overflow-y: auto;
}

.folder-list {
  max-height: 300px;
}

.folder-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background-color 0.15s;
}

.folder-option:active {
  background-color: #F5F5F5;
}

.folder-option.selected {
  background-color: rgba(74, 111, 232, 0.08);
}

.check-icon {
  color: #4A6FE8;
  font-size: 18px;
  font-weight: 700;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn-primary, .btn-secondary {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  transition: opacity 0.15s;
}

.btn-primary {
  background-color: #4A6FE8;
  color: #FFFFFF;
}

.btn-secondary {
  background-color: #F2F2F7;
  color: #1A1A1A;
}

.btn-primary:active, .btn-secondary:active {
  opacity: 0.7;
}

.folder-name-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  font-size: 16px;
}
```

## 5. 核心业务逻辑（list.js）

```javascript
// ========== "+" 按钮点击 ==========
showUploadMenu() {
  this.setData({ showUploadSheet: true })
},

hideUploadSheet() {
  this.setData({ showUploadSheet: false })
},

// ========== 上传文件 ==========
handleUploadFile() {
  this.setData({ showUploadSheet: false })

  wx.chooseMessageFile({
    count: 1,
    type: 'file',
    extension: ['mp3', 'm4a', 'wav'],
    success: (res) => {
      const file = res.tempFiles[0]

      // 检查文件大小（500MB）
      if (file.size > 500 * 1024 * 1024) {
        showToast('文件大小不能超过 500MB', 'error')
        return
      }

      // 提取音频时长
      this.extractAudioDuration(file.path, (duration) => {
        // 保存临时文件信息
        this.setData({
          tempSelectedFile: {
            path: file.path,
            name: file.name,
            size: file.size,
            duration: duration
          },
          showFolderSelector: true
        })
      })
    },
    fail: (err) => {
      console.error('选择文件失败:', err)
      showToast('文件选择失败', 'error')
    }
  })
},

// 提取音频时长
extractAudioDuration(filePath, callback) {
  const audio = wx.createInnerAudioContext()
  audio.src = filePath

  audio.onCanplay(() => {
    const duration = Math.floor(audio.duration)
    audio.destroy()
    callback(duration)
  })

  audio.onError((err) => {
    console.error('音频加载失败:', err)
    audio.destroy()
    callback(0)
  })
},

// ========== 知识库选择 ==========
selectFolderForUpload(e) {
  const folderId = e.currentTarget.dataset.id
  const folderName = e.currentTarget.dataset.name

  this.setData({
    currentFolderId: folderId,
    currentFolderName: folderName
  })
},

confirmFolderSelection() {
  this.setData({ showFolderSelector: false })

  // 跳转到上传页面
  const file = this.data.tempSelectedFile
  wx.navigateTo({
    url: `/pages/meeting/upload?fileName=${file.name}&duration=${file.duration}&folderId=${this.data.currentFolderId || ''}`
  })

  // 传递文件路径（通过全局变量或事件总线）
  getApp().globalData.uploadFile = file
},

// ========== 新建知识库 ==========
handleCreateFolder() {
  this.setData({
    showUploadSheet: false,
    showFolderSelector: false,
    showCreateFolder: true,
    newFolderName: ''
  })
},

hideCreateFolder() {
  this.setData({ showCreateFolder: false })
},

onFolderNameInput(e) {
  this.setData({ newFolderName: e.detail.value })
},

async confirmCreateFolder() {
  const name = this.data.newFolderName.trim()

  if (!name) {
    showToast('请输入知识库名称', 'error')
    return
  }

  try {
    showLoading('创建中...')
    const newFolder = await API.createFolder({ name })

    // 更新本地列表
    const folders = [...this.data.folders, newFolder]
    this.setData({
      folders,
      showCreateFolder: false,
      newFolderName: ''
    })

    hideLoading()
    showToast('知识库创建成功', 'success')
  } catch (error) {
    console.error('创建知识库失败:', error)
    hideLoading()
    showToast('创建失败，请重试', 'error')
  }
},

// ========== 抽屉选择联动 ==========
selectFolder(e) {
  const folderId = e.currentTarget.dataset.id
  const folder = this.data.folders.find(f => f.id === folderId)

  this.setData({
    currentFolderId: folderId,
    currentFolderName: folder ? folder.name : '录音文件',
    showDrawer: false
  })

  // 重新加载列表
  this.loadMeetingList(true)
}
```

## 6. 文件修改清单

### 前端文件
- ✅ `pages/meeting/list.wxml` - 添加 ActionSheet、知识库选择 Modal、新建知识库 Modal
- ✅ `pages/meeting/list.wxss` - 添加 Modal 样式、优化 ActionSheet 样式
- ✅ `pages/meeting/list.js` - 核心业务逻辑实现
- ✅ `pages/meeting/upload.wxml` - 修改进度页文案
- ✅ `pages/meeting/upload.wxss` - 样式微调（如需要）
- ✅ `pages/meeting/upload.js` - OSS 上传逻辑 + 进度监听
- ✅ `utils/api.js` - 添加 `createFolder()` 和 `getFolders()` 方法

### 后端文件
- ⚠️ `backend/app/api/folders.py` - 新建（知识库 CRUD API）
- ⚠️ `backend/app/models.py` - 添加 `Folder` 模型（如不存在）
- ⚠️ `backend/app/api/meeting.py` - 修改创建接口，支持 `folder_id` 参数

### 数据库迁移
- ⚠️ `backend/migrations/add_folders.py` - 创建 `folders` 表
- ⚠️ `backend/migrations/add_meeting_folder_id.py` - 为 `meetings` 表添加 `folder_id` 字段

## 7. 实现优先级

### P0 - 核心流程（第一阶段）
1. ✅ 点击 "+" 按钮显示 ActionSheet
2. ✅ 选择 "上传文件" → 文件选择器
3. ✅ 知识库选择页面（使用当前 folders 模拟数据）
4. ✅ 跳转上传页面 + OSS 上传 + 进度显示
5. ✅ 修改上传页面文案（"上传中" / "正在上传文件到云端"）

### P1 - 知识库管理（第二阶段）
1. ⚠️ 新建知识库 Modal UI
2. ⚠️ 后端 API 开发（Folder CRUD）
3. ⚠️ 前端集成后端 API
4. ⚠️ 抽屉选择联动更新 `currentFolderId`
5. ⚠️ 会议列表按 `folder_id` 筛选

### P2 - 优化与完善（第三阶段）
1. ⚠️ 错误处理（文件格式/大小校验）
2. ⚠️ 上传失败重试机制
3. ⚠️ 音频时长提取异常处理
4. ⚠️ 知识库列表排序和搜索
5. ⚠️ 知识库重命名和删除功能

## 8. 测试要点

### 功能测试
- [ ] 点击 "+" 按钮正常弹出 ActionSheet
- [ ] 选择 "上传文件" 正常打开文件选择器
- [ ] 选择音频文件后正常显示知识库选择页
- [ ] 知识库选择页显示当前知识库和列表
- [ ] 点击 "确认" 正常跳转到上传页面
- [ ] 上传页面正确显示文件信息和进度
- [ ] 上传完成后正常返回列表并刷新
- [ ] 选择 "新建知识库" 正常弹出输入框
- [ ] 输入名称后正常创建知识库
- [ ] 抽屉选择文件夹正常更新状态

### 边界测试
- [ ] 文件大小超过 500MB 正常提示
- [ ] 选择非音频文件正常拦截
- [ ] 网络异常时上传失败处理
- [ ] 知识库名称为空时提示
- [ ] 知识库名称过长时截断
- [ ] 音频时长提取失败时兜底

### UI 测试
- [ ] ActionSheet 动画流畅
- [ ] Modal 显示/隐藏动画正常
- [ ] 进度条平滑更新
- [ ] 适配 iPhone X 及以上安全区
- [ ] 深色模式兼容（如需要）

## 9. 注意事项

### 开发规范
- 所有新增 UI 组件必须遵循 TicNote 设计风格
- 复用现有的 CSS 变量和样式
- 保持代码风格与现有代码一致
- 添加详细的注释说明

### 性能优化
- 文件选择后立即提取时长，避免用户等待
- 上传进度实时更新，不超过 100ms 间隔
- 知识库列表较长时使用虚拟滚动（可选）

### 用户体验
- 所有异步操作显示 Loading 状态
- 错误提示清晰友好
- 操作成功后及时反馈
- 避免频繁弹窗打扰用户

### 安全性
- 文件类型和大小严格校验
- OSS 上传使用临时签名 URL
- 用户输入进行 XSS 防护
- 敏感操作添加二次确认

---

**文档版本**: v1.0
**最后更新**: 2025-11-09
**负责人**: Claude & Cosmos
**预计完成时间**: 第一阶段 2 天，第二阶段 3 天，第三阶段 2 天
