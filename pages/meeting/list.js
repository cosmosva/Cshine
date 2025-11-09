/**
 * 会议纪要列表页 - 知识库 v2
 */

const API = require('../../utils/api')
const { showToast, showLoading, hideLoading } = require('../../utils/toast')
const { formatDateTime } = require('../../utils/format')

Page({
  data: {
    meetingList: [],
    page: 1,
    pageSize: 20,
    total: 0,
    loading: false,
    refreshing: false,  // 下拉刷新状态
    hasMore: true,
    
    // 筛选和排序
    currentFilter: 'all',  // all / favorite / processing / completed / failed
    currentSort: 'time',   // time / favorite
    filterLabel: '全部',
    
    filterOptions: [
      { label: '全部', value: 'all' },
      { label: '收藏', value: 'favorite' },
      { label: '处理中', value: 'processing' },
      { label: '已完成', value: 'completed' },
      { label: '失败', value: 'failed' }
    ],
    
    sortOptions: [
      { label: '时间倒序', value: 'time' },
      { label: '收藏优先', value: 'favorite' }
    ],
    
    // ActionSheet 显示状态
    showFilterSheet: false,
    showSortSheet: false,
    showUploadSheet: false,  // 上传操作 ActionSheet
    showFolderActions: false, // 知识库操作菜单 ✨新增
    
    // Modal 显示状态
    showFolderSelector: false,  // 知识库选择 Modal
    showCreateFolder: false,    // 新建知识库 Modal
    showRenameModal: false,     // 重命名 Modal ✨新增
    showDeleteConfirm: false,   // 删除确认 Modal ✨新增
    
    // 知识库管理状态 ✨新增
    selectedFolderId: null,     // 当前操作的知识库ID
    selectedFolderName: '',     // 当前操作的知识库名称
    renameFolderValue: '',      // 重命名输入值
    
    // 会议移动状态 ✨新增
    showMeetingActions: false,      // 会议操作菜单
    showMoveFolderSelector: false,  // 会议移动选择器
    movingMeetingId: null,          // 要移动的会议ID
    meetingCurrentFolderId: null,   // 会议当前所在知识库
    meetingCurrentFolderName: '',   // 会议当前知识库名称
    meetingTargetFolderId: null,    // 会议目标知识库ID
    
    // 侧边栏抽屉
    showDrawer: false,
    totalCount: 55,  // 模拟数据：总文件数
    folders: [
      { id: 1, name: '短视频', count: 6 },
      { id: 2, name: '大海', count: 1 },
      { id: 3, name: '日常工作', count: 3 },
      { id: 4, name: 'AI 共创', count: 2 },
      { id: 5, name: 'AKS', count: 4 },
      { id: 6, name: 'MFY', count: 1 },
      { id: 7, name: '注会', count: 1 },
      { id: 8, name: '期货', count: 7 }
    ],
    
    // 知识库状态
    currentFolderId: null,        // 当前选中的知识库ID (null = 全部)
    currentFolderName: '录音文件', // 当前知识库名称
    
    // 临时数据
    tempSelectedFile: null,  // 临时存储选中的文件信息
    newFolderName: '',       // 新建知识库名称输入
    
    // 状态文案映射
    statusTextMap: {
      'pending': '等待',
      'processing': '处理中',
      'completed': '完成',
      'failed': '失败'
    },
    
    // 空状态文案
    emptyText: '暂无会议纪要'
  },

  onLoad() {
    this.loadMeetingList()
  },

  onShow() {
    // 从详情页返回时刷新列表
    if (this._needRefresh) {
      this._needRefresh = false
      this.loadMeetingList(true)
    }
  },

  /**
   * 加载会议列表
   */
  async loadMeetingList(refresh = false) {
    if (this.data.loading) return
    
    // 如果是刷新，重置页码
    if (refresh) {
      this.setData({
        page: 1,
        meetingList: [],
        hasMore: true
      })
    }
    
    // 如果没有更多数据，不再加载
    if (!refresh && !this.data.hasMore) {
      return
    }
    
    this.setData({ loading: true })
    
    try {
      const params = {
        page: this.data.page,
        page_size: this.data.pageSize,
        sort_by: this.data.currentSort
      }
      
      // 添加筛选条件
      if (this.data.currentFilter === 'favorite') {
        params.is_favorite = true
      } else if (this.data.currentFilter !== 'all') {
        params.status = this.data.currentFilter
      }
      
      const listData = await API.getMeetingList(params)
      console.log('会议列表（已解包）:', listData)
      
      if (listData) {
        const newList = refresh ? listData.items : [...this.data.meetingList, ...listData.items]
        
        this.setData({
          meetingList: newList,
          total: listData.total,
          hasMore: newList.length < listData.total,
          page: this.data.page + 1
        })
      }
    } catch (error) {
      console.error('加载会议列表失败:', error)
      showToast('加载失败，请重试', 'error')
    } finally {
      this.setData({ loading: false })
    }
  },

  /**
   * 下拉刷新
   */
  async onPullDownRefresh() {
    this.setData({ refreshing: true })
    await this.loadMeetingList(true)
    this.setData({ refreshing: false })
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    this.loadMeetingList()
  },

  /**
   * 显示筛选菜单
   */
  showFilterMenu() {
    this.setData({ showFilterSheet: true })
  },

  /**
   * 隐藏筛选菜单
   */
  hideFilterSheet() {
    this.setData({ showFilterSheet: false })
  },

  /**
   * 选择筛选条件
   */
  selectFilter(e) {
    const value = e.currentTarget.dataset.value
    const label = e.currentTarget.dataset.label
    
    if (value === this.data.currentFilter) {
      this.hideFilterSheet()
      return
    }
    
    this.setData({
      currentFilter: value,
      filterLabel: label,
      showFilterSheet: false,
      emptyText: value === 'favorite' ? '暂无收藏的会议' : '暂无会议纪要'
    })
    
    this.loadMeetingList(true)
  },

  /**
   * 显示排序菜单
   */
  showSortMenu() {
    this.setData({ showSortSheet: true })
  },

  /**
   * 隐藏排序菜单
   */
  hideSortSheet() {
    this.setData({ showSortSheet: false })
  },

  /**
   * 选择排序方式
   */
  selectSort(e) {
    const value = e.currentTarget.dataset.value
    
    if (value === this.data.currentSort) {
      this.hideSortSheet()
      return
    }
    
    this.setData({
      currentSort: value,
      showSortSheet: false
    })
    
    this.loadMeetingList(true)
  },

  /**
   * 切换收藏
   */
  async toggleFavorite(e) {
    const meetingId = e.currentTarget.dataset.id
    const isFavorite = e.currentTarget.dataset.favorite
    
    try {
      await API.toggleMeetingFavorite(meetingId)
      
      // 更新本地列表
      const meetingList = this.data.meetingList.map(item => {
        if (item.id === meetingId) {
          return { ...item, is_favorite: !isFavorite }
        }
        return item
      })
      
      this.setData({ meetingList })
      
      showToast(isFavorite ? '已取消收藏' : '已收藏', 'success')
    } catch (error) {
      console.error('切换收藏失败:', error)
      showToast('操作失败，请重试', 'error')
    }
  },

  /**
   * 查看会议详情
   */
  // 跳转到录音页面
  goToRecord() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  viewMeeting(e) {
    const meetingId = e.currentTarget.dataset.id
    const status = e.currentTarget.dataset.status

    // 如果还在处理中，跳转到上传页查看进度
    if (status === 'processing' || status === 'pending') {
      wx.navigateTo({
        url: `/pages/meeting/upload?meetingId=${meetingId}&mode=view`
      })
    } else {
      // 已完成，跳转到详情页
      wx.navigateTo({
        url: `/pages/meeting/detail?id=${meetingId}`
      })
    }

    // 标记需要刷新
    this._needRefresh = true
  },

  /**
   * 格式化完整时间
   */
  formatFullTime(dateStr) {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  },

  /**
   * 格式化时长（参考截图格式：48m 1s）
   */
  formatDuration(seconds) {
    if (!seconds) return ''
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      if (mins > 0) {
        return `${hours}h ${mins}m ${secs}s`
      }
      return `${hours}h ${secs}s`
    }
    return `${minutes}m ${secs}s`
  },

  /**
   * ========== 侧边栏抽屉 ==========
   */
  // 切换抽屉显示/隐藏
  toggleDrawer() {
    this.setData({
      showDrawer: !this.data.showDrawer
    })
  },

  // 关闭抽屉
  closeDrawer() {
    this.setData({
      showDrawer: false
    })
  },

  // 选择文件夹
  selectFolder(e) {
    const folderId = e.currentTarget.dataset.id
    const folder = this.data.folders.find(f => f.id === folderId)
    
    this.setData({
      currentFolderId: folderId,
      currentFolderName: folder ? folder.name : '录音文件',
      showDrawer: false
    })
    
    // 重新加载列表 (按文件夹筛选)
    this.loadMeetingList(true)
  },

  /**
   * ========== 上传功能 ==========
   */
  
  // 显示上传菜单
  showUploadMenu() {
    this.setData({ showUploadSheet: true })
  },

  // 隐藏上传菜单
  hideUploadSheet() {
    this.setData({ showUploadSheet: false })
  },

  // 处理上传文件
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

  // 隐藏知识库选择器
  hideFolderSelector() {
    this.setData({ showFolderSelector: false })
  },

  // 选择知识库用于上传
  selectFolderForUpload(e) {
    const folderId = e.currentTarget.dataset.id
    const folderName = e.currentTarget.dataset.name

    this.setData({
      currentFolderId: folderId,
      currentFolderName: folderName
    })
  },

  // 确认知识库选择
  confirmFolderSelection() {
    this.setData({ showFolderSelector: false })

    // 跳转到上传页面
    const file = this.data.tempSelectedFile
    const fileName = encodeURIComponent(file.name)
    const folderId = this.data.currentFolderId || ''
    
    wx.navigateTo({
      url: `/pages/meeting/upload?fileName=${fileName}&duration=${file.duration}&folderId=${folderId}`
    })

    // 传递文件路径（通过全局变量）
    getApp().globalData.uploadFile = file
  },

  // 处理新建知识库（从上传 ActionSheet）
  handleCreateFolder() {
    this.setData({
      showUploadSheet: false,
      showFolderSelector: false,
      showCreateFolder: true,
      newFolderName: ''
    })
  },

  // 处理新建知识库（从知识库选择器）
  handleCreateFolderFromSelector() {
    this.setData({
      showFolderSelector: false,
      showCreateFolder: true,
      newFolderName: ''
    })
  },

  // 隐藏新建知识库 Modal
  hideCreateFolder() {
    this.setData({ showCreateFolder: false })
  },

  // 知识库名称输入
  onFolderNameInput(e) {
    this.setData({ newFolderName: e.detail.value })
  },

  // 确认创建知识库
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

  // ========== 知识库管理功能 ✨新增 ==========
  
  // 显示知识库操作菜单
  showFolderMenu(e) {
    const { id, name } = e.currentTarget.dataset
    console.log('显示知识库操作菜单:', id, name)
    this.setData({
      selectedFolderId: id,
      selectedFolderName: name,
      showFolderActions: true
    })
  },

  // 隐藏知识库操作菜单
  hideFolderActions() {
    this.setData({ showFolderActions: false })
  },

  // ========== 重命名知识库 ==========
  
  // 打开重命名 Modal
  handleRenameFolder() {
    this.setData({
      showFolderActions: false,
      showRenameModal: true,
      renameFolderValue: this.data.selectedFolderName
    })
  },

  // 隐藏重命名 Modal
  hideRenameModal() {
    this.setData({ showRenameModal: false })
  },

  // 重命名输入
  onRenameInput(e) {
    this.setData({ renameFolderValue: e.detail.value })
  },

  // 确认重命名
  async confirmRename() {
    const name = this.data.renameFolderValue.trim()
    const folderId = this.data.selectedFolderId

    if (!name) {
      showToast('请输入知识库名称', 'error')
      return
    }

    if (name === this.data.selectedFolderName) {
      // 名称未改变，直接关闭
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

  // ========== 删除知识库 ==========
  
  // 打开删除确认 Modal
  handleDeleteFolder() {
    this.setData({
      showFolderActions: false,
      showDeleteConfirm: true
    })
  },

  // 隐藏删除确认 Modal
  hideDeleteConfirm() {
    this.setData({ showDeleteConfirm: false })
  },

  // 确认删除
  async confirmDelete() {
    const folderId = this.data.selectedFolderId

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

  // ========== 会议移动功能 ✨新增 ==========
  
  // 会议长按事件
  onMeetingLongPress(e) {
    const { id, folderId, folderName } = e.currentTarget.dataset
    wx.vibrateShort() // 震动反馈
    
    this.setData({
      movingMeetingId: id,
      meetingCurrentFolderId: folderId || null,
      meetingCurrentFolderName: folderName || '录音文件',
      showMeetingActions: true
    })
  },

  // 隐藏会议操作菜单
  hideMeetingActions() {
    this.setData({ showMeetingActions: false })
  },

  // 打开移动到知识库选择器
  handleMoveToFolder() {
    this.setData({
      showMeetingActions: false,
      showMoveFolderSelector: true,
      meetingTargetFolderId: this.data.meetingCurrentFolderId
    })
  },

  // 隐藏移动选择器
  hideMoveFolderSelector() {
    this.setData({ showMoveFolderSelector: false })
  },

  // 选择目标知识库
  selectMoveTargetFolder(e) {
    const folderId = e.currentTarget.dataset.id
    this.setData({ meetingTargetFolderId: folderId })
  },

  // 确认移动会议
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

  // 从列表删除会议
  async handleDeleteMeetingFromList() {
    const meetingId = this.data.movingMeetingId
    
    // 先弹出确认对话框
    const res = await wx.showModal({
      title: '删除会议',
      content: '确定要删除这条会议纪要吗？',
      confirmText: '删除',
      confirmColor: '#FF3B30',
      cancelText: '取消'
    })

    if (!res.confirm) {
      this.setData({ showMeetingActions: false })
      return
    }

    try {
      showLoading('删除中...')
      await API.deleteMeeting(meetingId)
      
      hideLoading()
      showToast('删除成功', 'success')
      this.setData({ showMeetingActions: false })

      // 刷新列表
      await this.loadMeetingList(true)
    } catch (error) {
      console.error('删除会议失败:', error)
      hideLoading()
      showToast(error.message || '删除失败', 'error')
    }
  },

  // 阻止关闭
  preventClose() {
    // 空函数，用于阻止点击 Modal 内部关闭
  },

  /**
   * 阻止事件冒泡
   */
  preventDefault() {
    // 空函数，用于阻止滚动穿透
  }
})
