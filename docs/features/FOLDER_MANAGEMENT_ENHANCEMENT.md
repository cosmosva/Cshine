# 知识库管理功能完善 - 开发计划

> **版本**: v0.5.0  
> **优先级**: 建议🟡  
> **开发时间**: 2-3 天  
> **最后更新**: 2025-11-09

---

## 📋 目录

1. [功能概述](#1-功能概述)
2. [交互流程设计](#2-交互流程设计)
3. [UI 设计规范](#3-ui-设计规范)
4. [技术实现](#4-技术实现)
5. [后端 API](#5-后端-api)
6. [文件修改清单](#6-文件修改清单)
7. [测试计划](#7-测试计划)
8. [部署说明](#8-部署说明)

---

## 1. 功能概述

### 1.1 需求背景

v0.4.5 版本已实现知识库（文件夹）的基础功能：
- ✅ 创建知识库
- ✅ 列表展示
- ✅ 会议上传时选择知识库
- ✅ 按知识库筛选会议

但仍缺少以下核心管理功能：
- ❌ 重命名知识库
- ❌ 删除知识库（带确认）
- ❌ 移动会议到其他知识库
- ❌ 知识库详细统计信息

### 1.2 功能目标

本次开发将补齐以上功能，使知识库管理形成完整闭环，提升用户的内容组织效率。

### 1.3 用户价值

- **更灵活的组织方式**: 随时调整知识库名称和结构
- **避免误操作**: 删除时有确认机制，保护数据安全
- **便捷的内容管理**: 可以将会议移动到合适的分类
- **清晰的数据统计**: 了解每个知识库的使用情况

---

## 2. 交互流程设计

### 2.1 知识库重命名流程

```
抽屉中知识库卡片
    ↓
长按知识库卡片 / 点击更多图标（⋯）
    ↓
弹出操作菜单（ActionSheet）
    - 重命名
    - 删除
    - 取消
    ↓
点击 "重命名"
    ↓
弹出输入框 Modal
    - 标题："重命名知识库"
    - 输入框：当前名称预填充
    - 按钮：取消 / 确认
    ↓
输入新名称
    ↓
点击 "确认"
    ↓
调用后端 API 更新
    ↓
更新本地 data.folders
    ↓
Toast 提示："重命名成功"
    ↓
如果是当前选中的知识库，同步更新 currentFolderName
    ↓
关闭 Modal
```

### 2.2 知识库删除流程

```
抽屉中知识库卡片
    ↓
长按 / 点击更多图标（⋯）
    ↓
弹出操作菜单（ActionSheet）
    ↓
点击 "删除"
    ↓
弹出确认对话框 Modal
    - 标题："删除知识库"
    - 内容："确定要删除「{name}」吗？"
    - 说明："删除后，其中的会议将移至「录音文件」"
    - 按钮：取消 / 删除（红色）
    ↓
点击 "删除"
    ↓
调用后端 API 删除
    ↓
更新本地 data.folders（移除该项）
    ↓
如果当前选中的是该知识库
    → 切换到 "录音文件"（currentFolderId = null）
    → 重新加载会议列表
    ↓
Toast 提示："知识库已删除"
    ↓
关闭 Modal 和 ActionSheet
```

### 2.3 会议移动流程（方式一：会议详情页）

```
会议详情页
    ↓
点击右上角 "⋯" 更多菜单
    ↓
弹出操作菜单（ActionSheet）
    - 编辑会议
    - 移动到知识库
    - 删除会议
    - 取消
    ↓
点击 "移动到知识库"
    ↓
弹出知识库选择 Modal（复用上传时的选择器）
    - 标题："移动到知识库"
    - 当前知识库：高亮显示
    - 知识库列表
    - 按钮：取消 / 确认
    ↓
选择目标知识库
    ↓
点击 "确认"
    ↓
调用后端 API 更新会议的 folder_id
    ↓
Toast 提示："已移动到「{目标知识库}」"
    ↓
返回列表页并刷新
```

### 2.4 会议移动流程（方式二：列表页长按）

```
会议列表页
    ↓
长按会议卡片
    ↓
弹出快捷操作菜单（ActionSheet）
    - 查看详情
    - 移动到知识库
    - 删除
    - 取消
    ↓
点击 "移动到知识库"
    ↓
（后续流程同方式一）
```

### 2.5 知识库统计信息

```
抽屉中每个知识库卡片显示：
- 📁 图标 + 知识库名称
- 会议数量（右侧灰色小字）
- ⋯ 更多操作

点击知识库卡片（非⋯按钮）：
    → 筛选该知识库的会议
    → 关闭抽屉
    → 更新二级导航栏标题

点击⋯按钮：
    → 弹出操作菜单（重命名/删除）
```

---

## 3. UI 设计规范

### 3.1 知识库操作菜单（ActionSheet）

```xml
<!-- 知识库操作菜单 -->
<view class="action-sheet-mask" wx:if="{{showFolderActions}}" bindtap="hideFolderActions"></view>
<view class="action-sheet {{showFolderActions ? 'show' : ''}}">
  <view class="action-sheet-header">
    <text class="action-sheet-title">{{selectedFolderName}}</text>
    <view class="action-sheet-close" bindtap="hideFolderActions">✕</view>
  </view>
  <view class="action-sheet-body">
    <view class="action-item" bindtap="handleRenameFolder">
      <text class="action-icon">✏️</text>
      <text class="action-label">重命名</text>
    </view>
    <view class="action-item danger" bindtap="handleDeleteFolder">
      <text class="action-icon">🗑️</text>
      <text class="action-label">删除</text>
    </view>
  </view>
</view>
```

### 3.2 重命名 Modal

```xml
<!-- 重命名知识库 -->
<view class="modal-mask" wx:if="{{showRenameModal}}" catchtap="hideRenameModal"></view>
<view class="modal small {{showRenameModal ? 'show' : ''}}" catchtap="preventClose">
  <view class="modal-header">
    <text class="modal-title">重命名知识库</text>
  </view>
  <view class="modal-body">
    <input class="folder-name-input"
           placeholder="请输入新名称"
           value="{{renameFolderValue}}"
           bindinput="onRenameInput"
           maxlength="20"
           focus="{{showRenameModal}}" />
  </view>
  <view class="modal-footer">
    <view class="btn-secondary" bindtap="hideRenameModal">取消</view>
    <view class="btn-primary" bindtap="confirmRename">确认</view>
  </view>
</view>
```

### 3.3 删除确认 Modal

```xml
<!-- 删除确认 -->
<view class="modal-mask" wx:if="{{showDeleteConfirm}}" catchtap="hideDeleteConfirm"></view>
<view class="modal small {{showDeleteConfirm ? 'show' : ''}}" catchtap="preventClose">
  <view class="modal-header">
    <text class="modal-title">删除知识库</text>
  </view>
  <view class="modal-body">
    <text class="delete-warning">确定要删除「{{selectedFolderName}}」吗？</text>
    <text class="delete-note">删除后，其中的会议将移至「录音文件」</text>
  </view>
  <view class="modal-footer">
    <view class="btn-secondary" bindtap="hideDeleteConfirm">取消</view>
    <view class="btn-danger" bindtap="confirmDelete">删除</view>
  </view>
</view>
```

### 3.4 会议操作菜单（详情页和列表页）

```xml
<!-- 会议操作菜单（详情页） -->
<view class="action-sheet-mask" wx:if="{{showMeetingActions}}" bindtap="hideMeetingActions"></view>
<view class="action-sheet {{showMeetingActions ? 'show' : ''}}">
  <view class="action-sheet-header">
    <text class="action-sheet-title">操作</text>
    <view class="action-sheet-close" bindtap="hideMeetingActions">✕</view>
  </view>
  <view class="action-sheet-body">
    <view class="action-item" bindtap="handleEditMeeting">
      <text class="action-icon">✏️</text>
      <text class="action-label">编辑会议</text>
    </view>
    <view class="action-item" bindtap="handleMoveToFolder">
      <text class="action-icon">📁</text>
      <text class="action-label">移动到知识库</text>
    </view>
    <view class="action-item danger" bindtap="handleDeleteMeeting">
      <text class="action-icon">🗑️</text>
      <text class="action-label">删除会议</text>
    </view>
  </view>
</view>
```

### 3.5 会议移动知识库选择器

```xml
<!-- 会议移动：知识库选择 -->
<view class="modal-mask" wx:if="{{showMoveFolderSelector}}" bindtap="hideMoveFolderSelector"></view>
<view class="modal {{showMoveFolderSelector ? 'show' : ''}}">
  <view class="modal-header">
    <text class="modal-title">移动到知识库</text>
  </view>
  <view class="modal-body">
    <text class="current-folder-label">当前位置：{{meetingCurrentFolderName}}</text>

    <scroll-view class="folder-list" scroll-y>
      <!-- 录音文件（全部） -->
      <view class="folder-option {{meetingTargetFolderId === null ? 'selected' : ''}}"
            bindtap="selectMoveTargetFolder" data-id="{{null}}" data-name="录音文件">
        <text class="folder-name">📁 录音文件</text>
        <text class="check-icon" wx:if="{{meetingTargetFolderId === null}}">✓</text>
      </view>

      <!-- 用户创建的知识库 -->
      <view class="folder-option {{meetingTargetFolderId === item.id ? 'selected' : ''}}"
            wx:for="{{folders}}" wx:key="id"
            bindtap="selectMoveTargetFolder" data-id="{{item.id}}" data-name="{{item.name}}">
        <text class="folder-name">📁 {{item.name}}</text>
        <text class="check-icon" wx:if="{{meetingTargetFolderId === item.id}}">✓</text>
      </view>
    </scroll-view>

    <view class="modal-actions">
      <view class="btn-secondary" bindtap="hideMoveFolderSelector">取消</view>
      <view class="btn-primary" bindtap="confirmMoveToFolder">确认</view>
    </view>
  </view>
</view>
```

### 3.6 样式规范

```css
/* 危险操作样式 */
.action-item.danger {
  color: #FF3B30;
}

.action-item.danger .action-icon {
  opacity: 1;
}

.btn-danger {
  flex: 1;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  background-color: #FF3B30;
  color: #FFFFFF;
  transition: opacity 0.15s;
}

.btn-danger:active {
  opacity: 0.7;
}

/* 删除警告文案 */
.delete-warning {
  display: block;
  font-size: 16px;
  color: #1A1A1A;
  margin-bottom: 12px;
}

.delete-note {
  display: block;
  font-size: 14px;
  color: #8E8E93;
  line-height: 20px;
}

/* 当前位置标签 */
.current-folder-label {
  display: block;
  font-size: 14px;
  color: #8E8E93;
  margin-bottom: 12px;
}

/* 知识库更多操作按钮 */
.folder-more {
  padding: 6px;
  font-size: 18px;
  color: #8E8E93;
  transition: opacity 0.15s;
}

.folder-more:active {
  opacity: 0.5;
}
```

---

## 4. 技术实现

### 4.1 状态管理（pages/meeting/list.js）

```javascript
data: {
  // 现有状态
  folders: [],
  currentFolderId: null,
  currentFolderName: '录音文件',

  // 新增状态
  showFolderActions: false,       // 知识库操作菜单
  showRenameModal: false,          // 重命名 Modal
  showDeleteConfirm: false,        // 删除确认 Modal
  showMoveFolderSelector: false,   // 会议移动选择器

  selectedFolderId: null,          // 当前操作的知识库ID
  selectedFolderName: '',          // 当前操作的知识库名称
  renameFolderValue: '',           // 重命名输入值

  // 会议移动相关
  movingMeetingId: null,           // 要移动的会议ID
  meetingCurrentFolderId: null,    // 会议当前所在知识库
  meetingCurrentFolderName: '',    // 会议当前知识库名称
  meetingTargetFolderId: null,     // 会议目标知识库ID
}
```

### 4.2 知识库重命名实现

```javascript
// ========== 显示知识库操作菜单 ==========
showFolderMenu(e) {
  const { id, name } = e.currentTarget.dataset
  this.setData({
    selectedFolderId: id,
    selectedFolderName: name,
    showFolderActions: true
  })
},

hideFolderActions() {
  this.setData({ showFolderActions: false })
},

// ========== 重命名知识库 ==========
handleRenameFolder() {
  this.setData({
    showFolderActions: false,
    showRenameModal: true,
    renameFolderValue: this.data.selectedFolderName
  })
},

hideRenameModal() {
  this.setData({ showRenameModal: false })
},

onRenameInput(e) {
  this.setData({ renameFolderValue: e.detail.value })
},

async confirmRename() {
  const name = this.data.renameFolderValue.trim()
  const folderId = this.data.selectedFolderId

  if (!name) {
    showToast('请输入知识库名称', 'error')
    return
  }

  if (name === this.data.selectedFolderName) {
    this.setData({ showRenameModal: false })
    return
  }

  try {
    showLoading('重命名中...')
    await API.updateFolder(folderId, { name })

    // 更新本地列表
    const folders = this.data.folders.map(f =>
      f.id === folderId ? { ...f, name } : f
    )
    this.setData({ folders })

    // 如果是当前选中的知识库，同步更新
    if (this.data.currentFolderId === folderId) {
      this.setData({ currentFolderName: name })
    }

    hideLoading()
    showToast('重命名成功', 'success')
    this.setData({ showRenameModal: false })
  } catch (error) {
    console.error('重命名失败:', error)
    hideLoading()
    showToast(error.message || '重命名失败', 'error')
  }
},
```

### 4.3 知识库删除实现

```javascript
// ========== 删除知识库 ==========
handleDeleteFolder() {
  this.setData({
    showFolderActions: false,
    showDeleteConfirm: true
  })
},

hideDeleteConfirm() {
  this.setData({ showDeleteConfirm: false })
},

async confirmDelete() {
  const folderId = this.data.selectedFolderId
  const folderName = this.data.selectedFolderName

  try {
    showLoading('删除中...')
    await API.deleteFolder(folderId)

    // 更新本地列表
    const folders = this.data.folders.filter(f => f.id !== folderId)
    this.setData({ folders })

    // 如果删除的是当前选中的知识库，切换到"录音文件"
    if (this.data.currentFolderId === folderId) {
      this.setData({
        currentFolderId: null,
        currentFolderName: '录音文件'
      })
      // 重新加载会议列表
      await this.loadMeetingList(true)
    }

    hideLoading()
    showToast('知识库已删除', 'success')
    this.setData({ showDeleteConfirm: false })
  } catch (error) {
    console.error('删除失败:', error)
    hideLoading()
    showToast(error.message || '删除失败', 'error')
  }
},
```

### 4.4 会议移动实现（列表页）

```javascript
// ========== 会议长按菜单 ==========
onMeetingLongPress(e) {
  const { id, folderId, folderName } = e.currentTarget.dataset
  
  this.setData({
    movingMeetingId: id,
    meetingCurrentFolderId: folderId,
    meetingCurrentFolderName: folderName || '录音文件',
    showMeetingActions: true
  })
},

hideMeetingActions() {
  this.setData({ showMeetingActions: false })
},

// ========== 移动到知识库 ==========
handleMoveToFolder() {
  this.setData({
    showMeetingActions: false,
    showMoveFolderSelector: true,
    meetingTargetFolderId: this.data.meetingCurrentFolderId
  })
},

hideMoveFolderSelector() {
  this.setData({ showMoveFolderSelector: false })
},

selectMoveTargetFolder(e) {
  const folderId = e.currentTarget.dataset.id
  this.setData({ meetingTargetFolderId: folderId })
},

async confirmMoveToFolder() {
  const meetingId = this.data.movingMeetingId
  const targetFolderId = this.data.meetingTargetFolderId
  const currentFolderId = this.data.meetingCurrentFolderId

  // 如果目标知识库和当前一样，直接关闭
  if (targetFolderId === currentFolderId) {
    this.setData({ showMoveFolderSelector: false })
    return
  }

  try {
    showLoading('移动中...')
    await API.updateMeeting(meetingId, { folder_id: targetFolderId })

    // 获取目标知识库名称
    const targetFolderName = targetFolderId === null
      ? '录音文件'
      : this.data.folders.find(f => f.id === targetFolderId)?.name || '知识库'

    hideLoading()
    showToast(`已移动到「${targetFolderName}」`, 'success')
    this.setData({ showMoveFolderSelector: false })

    // 刷新列表
    await this.loadMeetingList(true)
  } catch (error) {
    console.error('移动失败:', error)
    hideLoading()
    showToast(error.message || '移动失败', 'error')
  }
},
```

### 4.5 会议移动实现（详情页 - pages/meeting/detail.js）

```javascript
// ========== 详情页更多操作 ==========
showMoreActions() {
  this.setData({ showMeetingActions: true })
},

hideMeetingActions() {
  this.setData({ showMeetingActions: false })
},

// ========== 移动到知识库（详情页） ==========
async handleMoveToFolder() {
  // 先获取知识库列表（如果还没有）
  if (!this.data.folders || this.data.folders.length === 0) {
    try {
      const foldersData = await API.getFolders()
      this.setData({ folders: foldersData.items || foldersData })
    } catch (error) {
      console.error('获取知识库列表失败:', error)
    }
  }

  this.setData({
    showMeetingActions: false,
    showMoveFolderSelector: true,
    meetingCurrentFolderId: this.data.meeting.folder_id,
    meetingTargetFolderId: this.data.meeting.folder_id
  })
},

// 选择目标知识库（同列表页）
selectMoveTargetFolder(e) {
  const folderId = e.currentTarget.dataset.id
  this.setData({ meetingTargetFolderId: folderId })
},

// 确认移动（同列表页，但详情页需要更新本页数据）
async confirmMoveToFolder() {
  const meetingId = this.data.meeting.id
  const targetFolderId = this.data.meetingTargetFolderId
  const currentFolderId = this.data.meetingCurrentFolderId

  if (targetFolderId === currentFolderId) {
    this.setData({ showMoveFolderSelector: false })
    return
  }

  try {
    showLoading('移动中...')
    await API.updateMeeting(meetingId, { folder_id: targetFolderId })

    const targetFolderName = targetFolderId === null
      ? '录音文件'
      : this.data.folders.find(f => f.id === targetFolderId)?.name || '知识库'

    // 更新本页数据
    this.setData({
      'meeting.folder_id': targetFolderId,
      showMoveFolderSelector: false
    })

    hideLoading()
    showToast(`已移动到「${targetFolderName}」`, 'success')
  } catch (error) {
    console.error('移动失败:', error)
    hideLoading()
    showToast(error.message || '移动失败', 'error')
  }
},
```

---

## 5. 后端 API

### 5.1 已有 API（无需修改）

```
PUT /api/v1/folders/{folder_id}
DELETE /api/v1/folders/{folder_id}
PUT /api/v1/meeting/{meeting_id}
```

后端 API 已在 v0.4.5 实现，本次只需前端集成。

### 5.2 API 调用示例（utils/api.js）

```javascript
// 已有的 API 方法，无需新增
updateFolder(folderId, data) {
  return request({
    url: `/folders/${folderId}`,
    method: 'PUT',
    data
  })
},

deleteFolder(folderId) {
  return request({
    url: `/folders/${folderId}`,
    method: 'DELETE'
  })
},

updateMeeting(meetingId, data) {
  return request({
    url: `/meeting/${meetingId}`,
    method: 'PUT',
    data
  })
}
```

---

## 6. 文件修改清单

### 前端文件

#### 修改文件
- ✅ `pages/meeting/list.wxml` - 添加知识库操作菜单、重命名/删除 Modal、会议移动选择器
- ✅ `pages/meeting/list.wxss` - 添加新 UI 组件样式
- ✅ `pages/meeting/list.js` - 实现知识库管理和会议移动逻辑
- ✅ `pages/meeting/detail.wxml` - 添加会议操作菜单、移动选择器
- ✅ `pages/meeting/detail.wxss` - 添加新 UI 组件样式
- ✅ `pages/meeting/detail.js` - 实现会议移动逻辑

#### 新增文件
- 📝 `docs/features/FOLDER_MANAGEMENT_ENHANCEMENT.md` - 本文档

### 后端文件
- ❌ 无需修改（API 已在 v0.4.5 实现）

---

## 7. 测试计划

### 7.1 功能测试

**知识库重命名**
- [ ] 点击知识库⋯按钮显示操作菜单
- [ ] 点击重命名显示输入框，当前名称预填充
- [ ] 输入新名称并确认，成功更新
- [ ] 如果是当前选中知识库，标题同步更新
- [ ] 空名称提示错误
- [ ] 重复名称校验（后端返回错误）

**知识库删除**
- [ ] 点击删除显示确认对话框
- [ ] 确认后成功删除
- [ ] 删除当前选中知识库，自动切换到"录音文件"并刷新列表
- [ ] 删除后，相关会议的 folder_id 置空（后端逻辑）

**会议移动（列表页）**
- [ ] 长按会议卡片显示操作菜单
- [ ] 点击移动到知识库显示选择器
- [ ] 当前知识库高亮显示
- [ ] 选择新知识库并确认，成功移动
- [ ] 列表刷新，会议出现在新知识库下

**会议移动（详情页）**
- [ ] 点击详情页更多按钮显示操作菜单
- [ ] 点击移动到知识库显示选择器
- [ ] 确认移动后，详情页数据同步更新
- [ ] 返回列表页，会议位置已更改

### 7.2 边界测试

- [ ] 删除包含大量会议的知识库
- [ ] 移动会议到同一知识库（无操作）
- [ ] 网络异常时的错误处理
- [ ] 快速连续操作（防抖）
- [ ] 最后一个自定义知识库删除后

### 7.3 UI 测试

- [ ] 所有 Modal 动画流畅
- [ ] ActionSheet 显示/隐藏正常
- [ ] 危险操作（删除）使用红色高亮
- [ ] Toast 提示清晰友好
- [ ] 适配 iPhone X 安全区

---

## 8. 部署说明

### 8.1 更新类型
**功能增强** - 知识库管理完善

### 8.2 更新优先级
**建议🟡** - 用户可选择更新时间

### 8.3 数据库变更
**无** - 使用现有表结构

### 8.4 依赖变更
**无** - 使用现有依赖

### 8.5 环境变量变更
**无**

### 8.6 部署步骤

#### 前端部署
1. 微信开发者工具编译
2. 真机测试功能
3. 上传代码，版本号：**v0.5.0**
4. 提交审核

#### 后端部署
**无需部署** - 仅前端功能，后端 API 已在 v0.4.5 实现

### 8.7 验证方法

1. **知识库重命名验证**
```
1. 打开抽屉，点击任意知识库的⋯按钮
2. 选择"重命名"
3. 输入新名称，点击确认
4. 验证名称已更新，抽屉中显示新名称
```

2. **知识库删除验证**
```
1. 点击知识库⋯按钮，选择"删除"
2. 确认删除
3. 验证知识库从列表中消失
4. 验证其中的会议移至"录音文件"
```

3. **会议移动验证**
```
1. 长按会议卡片，选择"移动到知识库"
2. 选择目标知识库，确认
3. 验证会议出现在新知识库下
4. 验证原知识库中该会议消失
```

### 8.8 回滚方案

如遇问题，前端回滚到 v0.4.5 版本即可，无数据损失风险。

```bash
# 小程序回滚
1. 在微信公众平台选择 v0.4.5 版本
2. 点击"回退版本"
3. 无需后端操作
```

---

## 9. 注意事项

### 9.1 用户体验
- 删除操作必须有确认对话框，防止误操作
- 移动会议后，列表应自动刷新
- 所有异步操作显示 Loading 状态
- 错误提示友好清晰

### 9.2 数据安全
- 删除知识库不删除会议，只是将 folder_id 置空
- 后端已实现 ON DELETE SET NULL 约束
- 前端应同步更新本地状态

### 9.3 性能考虑
- 知识库列表较少时无需优化
- 会议移动后，只刷新受影响的列表
- 避免频繁调用 API

---

**文档版本**: v1.0  
**创建日期**: 2025-11-09  
**负责人**: Claude & Cosmos  
**预计完成**: 2-3 天

---

**Let Your Ideas Shine. ✨**

