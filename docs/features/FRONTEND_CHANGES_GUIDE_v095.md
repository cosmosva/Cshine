# 前端修改指南 - AI 调度逻辑优化 (v0.9.5)

## 概述

本文档说明前端需要进行的修改，以配合后端 AI 调度逻辑优化（v0.9.5）。

**核心变化：**
- 上传会议时不再选择 AI 模型
- 在详情页点击"立即生成"时才弹出 AI 模型选择器
- 调用新的后端接口 `POST /api/v1/meeting/{id}/generate-summary`

---

## 修改文件清单

### 1. `miniprogram/pages/meeting/list.js` - 会议列表页

**需要移除的代码：**

```javascript
// 第477-514行：handleUploadFile() 中的 AI 模型选择逻辑
// 移除：this.setData({ showAiModelPicker: true })

// 第534-541行：confirmFolderSelection()
// 移除：this.setData({ showAiModelPicker: true })
// 改为：直接调用 this.uploadAudioFile()

// 第543-560行：onAiModelConfirm()
// 完全移除此方法

// data 中移除：
//   selectedAiModelId: null,
//   selectedAiModelName: null,
//   showAiModelPicker: false
```

**修改后的代码示例：**

```javascript
// list.js 第534行左右
confirmFolderSelection() {
  const selectedFolderId = this.data.uploadTargetFolderId
  const selectedFolderName = this.data.uploadTargetFolderName

  console.log('[知识库选择] 已确认:', {
    folderId: selectedFolderId,
    folderName: selectedFolderName
  })

  // 关闭知识库选择器
  this.setData({
    showUploadFolderSelector: false
  })

  // ✅ 直接上传文件（不再选择 AI 模型）
  const file = this.data.tempSelectedFile
  this.uploadAudioFile(file, selectedFolderId)
},

// list.js 第567行左右
async uploadAudioFile(file, folderId) {
  wx.showLoading({ title: '上传中...', mask: true })

  try {
    const params = {
      title: file.name
    }

    // 添加知识库ID（如果有）
    if (folderId && folderId !== '') {
      params.folder_id = String(folderId)
    }

    // ✅ 移除 AI 模型ID参数
    // if (this.data.selectedAiModelId) {
    //   params.ai_model_id = this.data.selectedAiModelId
    // }

    // 调用合并接口
    const result = await API.uploadAudioAndCreateMeeting(file.path, params)

    wx.hideLoading()
    wx.showToast({
      title: '上传成功',
      icon: 'success',
      duration: 2000
    })

    // ✅ 立即跳转到详情页
    const meetingId = result.id || result.meeting_id
    setTimeout(() => {
      wx.navigateTo({
        url: `/pages/meeting/detail?id=${meetingId}`
      })
    }, 500)

  } catch (error) {
    wx.hideLoading()
    wx.showToast({
      title: error.message || '上传失败',
      icon: 'none',
      duration: 2000
    })
  }
}
```

---

### 2. `miniprogram/pages/meeting/list.wxml` - 会议列表页模板

**需要移除的代码：**

```xml
<!-- 移除 AI 模型选择器组件 -->
<ai-model-picker
  show="{{showAiModelPicker}}"
  bind:confirm="onAiModelConfirm"
  bind:cancel="onAiModelCancel"
/>
```

---

### 3. `miniprogram/pages/meeting/detail.js` - 会议详情页

**需要添加/修改的代码：**

```javascript
// detail.js - data 部分
data: {
  meeting: null,
  loading: true,
  showAiModelPicker: false,  // ✅ 新增：AI 模型选择器显示状态
  selectedAiModelId: null,   // ✅ 新增：选中的 AI 模型ID
  selectedAiModelName: null, // ✅ 新增：选中的 AI 模型名称
  statusTimer: null,
  // ... 其他字段
},

// detail.js - 第265-299行：修改 startProcessing() 方法
async startProcessing() {
  const meeting = this.data.meeting

  if (!meeting || !meeting.id) {
    wx.showToast({ title: '会议信息不完整', icon: 'none' })
    return
  }

  // ✅ 新逻辑：先弹出 AI 模型选择器
  this.setData({ showAiModelPicker: true })
},

// ✅ 新增：AI 模型选择确认回调
async onAiModelConfirm(e) {
  const { id, name } = e.detail

  this.setData({
    selectedAiModelId: id,
    selectedAiModelName: name,
    showAiModelPicker: false
  })

  console.log('[AI 模型选择] 已确认:', { id, name })

  // 开始生成总结
  await this.generateSummary(id)
},

// ✅ 新增：AI 模型选择取消回调
onAiModelCancel() {
  this.setData({ showAiModelPicker: false })
},

// ✅ 新增：生成总结方法
async generateSummary(aiModelId) {
  const meeting = this.data.meeting

  try {
    wx.showLoading({ title: '启动中...', mask: true })

    // 调用新接口 generate-summary
    await API.generateMeetingSummary(meeting.id, aiModelId)

    wx.hideLoading()
    wx.showToast({
      title: '开始处理',
      icon: 'success',
      duration: 1500
    })

    // 更新状态为 processing
    this.setData({ 'meeting.status': 'processing' })

    // 开始轮询状态
    this.startStatusPolling()

  } catch (error) {
    wx.hideLoading()
    wx.showToast({
      title: error.message || '启动失败',
      icon: 'none',
      duration: 2000
    })
  }
},

// detail.js - 轮询状态（保持不变）
startStatusPolling() {
  console.log('[状态轮询] 开始轮询')

  // 清除旧的定时器
  if (this.statusTimer) {
    clearInterval(this.statusTimer)
  }

  // 立即查询一次
  this.checkProcessingStatus()

  // 每 3 秒轮询一次
  this.statusTimer = setInterval(() => {
    this.checkProcessingStatus()
  }, 3000)
},

async checkProcessingStatus() {
  try {
    const meeting = this.data.meeting
    const status = await API.getMeetingStatus(meeting.id)

    console.log('[状态轮询] 当前状态:', status)

    // 如果状态变为 completed 或 failed，停止轮询并刷新详情
    if (status.status === 'completed' || status.status === 'failed') {
      console.log('[状态轮询] 处理完成，停止轮询')

      if (this.statusTimer) {
        clearInterval(this.statusTimer)
        this.statusTimer = null
      }

      // 刷新详情页
      await this.loadMeetingDetail()

      wx.showToast({
        title: status.status === 'completed' ? '处理完成' : '处理失败',
        icon: status.status === 'completed' ? 'success' : 'none',
        duration: 2000
      })
    }
  } catch (error) {
    console.error('[状态轮询] 查询失败:', error)
  }
}
```

---

### 4. `miniprogram/pages/meeting/detail.wxml` - 会议详情页模板

**需要添加的代码：**

```xml
<!-- detail.wxml - 在页面底部添加 AI 模型选择器 -->
<ai-model-picker
  show="{{showAiModelPicker}}"
  bind:confirm="onAiModelConfirm"
  bind:cancel="onAiModelCancel"
/>
```

---

### 5. `miniprogram/utils/api.js` - API 接口层

**需要添加的方法：**

```javascript
// api.js - 在 meeting 相关接口部分添加

/**
 * 生成会议总结（新版）
 * @param {string} meetingId - 会议ID
 * @param {string} aiModelId - AI 模型ID
 */
async generateMeetingSummary(meetingId, aiModelId) {
  return request({
    url: `/meeting/${meetingId}/generate-summary`,
    method: 'POST',
    data: {
      ai_model_id: aiModelId
    }
  })
},
```

---

## 修改步骤总结

### 步骤 1：修改会议列表页上传流程

1. 打开 [miniprogram/pages/meeting/list.js](../../miniprogram/pages/meeting/list.js)
2. 在 `data` 部分移除：
   - `selectedAiModelId`
   - `selectedAiModelName`
   - `showAiModelPicker`
3. 修改 `confirmFolderSelection()` 方法：直接调用 `this.uploadAudioFile()`
4. 删除 `onAiModelConfirm()` 和 `onAiModelCancel()` 方法
5. 修改 `uploadAudioFile()` 方法：移除 `ai_model_id` 参数

### 步骤 2：修改会议列表页模板

1. 打开 [miniprogram/pages/meeting/list.wxml](../../miniprogram/pages/meeting/list.wxml)
2. 移除 `<ai-model-picker>` 组件

### 步骤 3：修改会议详情页逻辑

1. 打开 [miniprogram/pages/meeting/detail.js](../../miniprogram/pages/meeting/detail.js)
2. 在 `data` 部分添加：
   - `showAiModelPicker: false`
   - `selectedAiModelId: null`
   - `selectedAiModelName: null`
3. 修改 `startProcessing()` 方法：改为弹出 AI 模型选择器
4. 添加 `onAiModelConfirm(e)` 方法
5. 添加 `onAiModelCancel()` 方法
6. 添加 `generateSummary(aiModelId)` 方法

### 步骤 4：修改会议详情页模板

1. 打开 [miniprogram/pages/meeting/detail.wxml](../../miniprogram/pages/meeting/detail.wxml)
2. 在页面底部添加 `<ai-model-picker>` 组件

### 步骤 5：添加新的 API 方法

1. 打开 [miniprogram/utils/api.js](../../miniprogram/utils/api.js)
2. 在 meeting 相关接口部分添加 `generateMeetingSummary(meetingId, aiModelId)` 方法

---

## 测试检查清单

### 上传流程测试

- [ ] 点击上传文件 → 选择音频 → 选择知识库 → 直接上传成功
- [ ] 上传成功后自动跳转到详情页
- [ ] 详情页显示会议基本信息（标题、时长等）
- [ ] 详情页显示"立即生成"按钮

### 生成总结流程测试

- [ ] 点击"立即生成"按钮 → 弹出 AI 模型选择器
- [ ] 选择 AI 模型并确认 → 开始处理
- [ ] 显示"开始处理"提示
- [ ] 状态轮询正常工作（每3秒查询一次）
- [ ] 处理完成后刷新详情页，显示完整内容

### 错误处理测试

- [ ] 取消 AI 模型选择 → 关闭选择器，不进行任何操作
- [ ] 网络错误时显示错误提示
- [ ] 处理失败时显示失败状态

---

## 关键变化总结

| 项目 | 旧版 | 新版 (v0.9.5) |
|------|------|---------------|
| **上传时机** | 选择文件 → 选择知识库 → **选择 AI 模型** → 上传 | 选择文件 → 选择知识库 → 上传 |
| **AI 模型选择** | 上传时选择 | 详情页点击"立即生成"时选择 |
| **调用接口** | `POST /api/v1/meeting/create` (带 `ai_model_id`) | `POST /api/v1/meeting/create` (不带 `ai_model_id`) |
| **生成总结接口** | `POST /api/v1/meeting/{id}/reprocess` | `POST /api/v1/meeting/{id}/generate-summary` (新接口) |
| **处理阶段** | 一次性处理（转录+总结） | 两阶段处理（转录 → 总结） |

---

## 注意事项

1. **兼容性**：旧版 `/reprocess` 接口仍然保留，但建议使用新版 `/generate-summary`
2. **状态轮询**：保持不变，仍然每3秒轮询一次
3. **UI 组件**：`ai-model-picker` 组件从列表页移到详情页
4. **用户体验**：上传速度更快（不等待 AI 处理），用户可以选择是否生成总结

---

## 常见问题

### Q1: 为什么要修改 AI 调度逻辑？

**A**: 原来的逻辑是上传时就选择 AI 模型并立即开始处理，导致：
- 上传流程冗长（需要选择 AI 模型）
- 用户无法选择是否生成总结
- 通义听悟既做转录又做总结，功能耦合

新版改为两阶段处理：
- 上传时只上传音频，速度更快
- 用户在详情页选择是否生成总结
- 通义听悟只负责转录，LLM 负责总结，职责清晰

### Q2: 旧会议数据会受影响吗？

**A**: 不会。旧会议数据保留，只是 `conversational_summary` 字段被移除（数据库迁移时清空）。

### Q3: 如果用户上传后不点"立即生成"会怎样？

**A**: 会议保持 PENDING 状态，用户可以随时回来点击"立即生成"开始处理。

---

## 相关文档

- [CLAUDE.md](../../CLAUDE.md) - 项目开发指南
- [CHANGELOG.md](../core/CHANGELOG.md) - 版本更新记录
- [backend/app/services/meeting_processor.py](../../backend/app/services/meeting_processor.py) - 后端处理逻辑
- [backend/app/api/meeting.py](../../backend/app/api/meeting.py) - 后端 API 接口
