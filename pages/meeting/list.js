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
    
    // 知识库管理状态 ✨新增
    selectedFolderId: null,     // 当前操作的知识库ID
    selectedFolderName: '',     // 当前操作的知识库名称
    
    // 会议操作状态 ✨新增
    movingMeetingId: null,          // 要操作的会议ID
    movingMeetingTitle: '',         // 要操作的会议标题
    meetingCurrentFolderId: null,   // 会议当前所在知识库
    meetingCurrentFolderName: '',   // 会议当前知识库名称
    
    // 知识库选择器状态
    showFolderSelector: false,      // 显示知识库选择器
    folderSelectorAction: '',       // 'copy' 或 'move'
    selectedTargetFolderId: null,   // 选中的目标知识库ID
    
    // 侧边栏抽屉
    showDrawer: false,
    totalCount: 0,  // 总文件数（从 API 获取）
    folders: [],    // 知识库列表（从 API 加载）
    
    // 知识库状态
    currentFolderId: 'uncategorized',  // 当前选中的知识库ID ('uncategorized' = 未分类, 数字ID = 指定知识库, null = 不筛选)
    currentFolderName: '录音文件',     // 当前知识库名称
    
    // 临时数据
    tempSelectedFile: null,  // 临时存储选中的文件信息
    
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
    this.loadFolderList()  // 加载知识库列表
    this.loadMeetingList() // 加载会议列表
  },

  onShow() {
    // 从详情页返回时刷新列表
    if (this._needRefresh) {
      this._needRefresh = false
      this.loadMeetingList(true)
    }
  },

  /**
   * 加载知识库列表
   */
  async loadFolderList() {
    try {
      console.log('开始加载知识库列表...')
      const response = await API.getFolders()
      console.log('知识库列表加载成功:', response)

      // 后端返回的是 { items: [...], total_count: N } 格式
      const folders = response?.items || response || []

      // total_count = 未分类的会议数量（folder_id 为 null）
      // 如果后端返回了 total_count，使用它；否则通过 API 获取
      let totalCount = response?.total_count

      if (totalCount === undefined) {
        // 如果后端没有返回 total_count，调用会议列表 API 获取未分类数量
        try {
          const listData = await API.getMeetingList({
            page: 1,
            page_size: 1,
            folder_id: 'uncategorized' // 查询未分类的会议
          })
          totalCount = listData?.total || 0
        } catch (err) {
          console.error('获取未分类数量失败:', err)
          totalCount = 0
        }
      }

      // 更新知识库列表
      this.setData({
        folders: folders,
        totalCount: totalCount
      })

      console.log(`知识库列表更新完成，共 ${folders.length} 个知识库，总计 ${totalCount} 个文件`)
    } catch (error) {
      console.error('加载知识库列表失败:', error)
      // 静默失败，不影响主流程
      this.setData({ folders: [], totalCount: 0 })
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

      // 添加知识库筛选
      if (this.data.currentFolderId !== null) {
        if (this.data.currentFolderId === 'uncategorized') {
          // 查询未分类的会议
          params.folder_id = 'uncategorized'
        } else {
          // 查询指定知识库的会议
          params.folder_id = this.data.currentFolderId
        }
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

  // 选择全部文件（录音文件 - 未分类的会议）
  selectAllFiles() {
    this.setData({
      currentFolderId: 'uncategorized',
      currentFolderName: '录音文件',
      showDrawer: false
    })

    // 重新加载列表（显示未分类的会议）
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
    console.log('handleUploadFile 被触发')
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
    console.log('handleCreateFolder 被触发')
    
    // 关闭所有弹窗
    this.setData({
      showUploadSheet: false,
      showFolderSelector: false
    })
    
    // 使用微信原生 Modal
    wx.showModal({
      title: '新建知识库',
      placeholderText: '请输入知识库名称',
      editable: true,
      confirmText: '确认',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          const name = (res.content || '').trim()
          console.log('用户输入的名称:', name)
          
          if (!name) {
            showToast('请输入知识库名称', 'error')
            return
          }
          
          // 创建知识库
          this.createFolderRequest(name)
        } else {
          console.log('用户取消了')
        }
      }
    })
  },

  // 处理新建知识库（从知识库选择器）
  handleCreateFolderFromSelector() {
    this.setData({
      showFolderSelector: false
    })
    
    // 使用微信原生 Modal
    wx.showModal({
      title: '新建知识库',
      placeholderText: '请输入知识库名称',
      editable: true,
      confirmText: '确认',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          const name = (res.content || '').trim()
          
          if (!name) {
            showToast('请输入知识库名称', 'error')
            // 重新打开知识库选择器
            this.setData({ showFolderSelector: true })
            return
          }
          
          // 创建知识库
          this.createFolderRequest(name)
        } else {
          // 重新打开知识库选择器
          this.setData({ showFolderSelector: true })
        }
      }
    })
  },

  // 创建知识库请求（统一的创建逻辑）
  async createFolderRequest(name) {
    try {
      console.log('开始调用 API 创建知识库:', name)
      showLoading('创建中...')
      const newFolder = await API.createFolder({ name })
      console.log('API 返回结果:', newFolder)

      // 重新加载知识库列表
      await this.loadFolderList()

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
    const { selectedFolderId, selectedFolderName } = this.data
    
    // 关闭操作菜单
    this.setData({ showFolderActions: false })
    
    // 使用微信原生 Modal
    wx.showModal({
      title: '重命名知识库',
      placeholderText: '请输入新名称',
      editable: true,
      content: selectedFolderName, // 预填充当前名称
      confirmText: '确认',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          const name = (res.content || '').trim()
          
          if (!name) {
            showToast('请输入知识库名称', 'error')
            return
          }
          
          if (name === selectedFolderName) {
            showToast('名称未改变', 'none')
            return
          }
          
          // 执行重命名
          this.renameFolderRequest(selectedFolderId, name)
        }
      }
    })
  },

  // 重命名知识库请求
  async renameFolderRequest(folderId, name) {
    try {
      showLoading('重命名中...')
      await API.updateFolder(folderId, { name })

      // 重新加载知识库列表
      await this.loadFolderList()

      // 如果是当前选中的知识库，同步更新
      if (this.data.currentFolderId === folderId) {
        this.setData({ currentFolderName: name })
      }

      hideLoading()
      showToast('重命名成功', 'success')
    } catch (error) {
      console.error('重命名失败:', error)
      hideLoading()
      showToast(error.message || '重命名失败', 'error')
    }
  },

  // ========== 删除知识库 ==========
  
  // 打开删除确认 Modal
  handleDeleteFolder() {
    const { selectedFolderId, selectedFolderName } = this.data
    
    // 关闭操作菜单
    this.setData({ showFolderActions: false })
    
    // 使用微信原生确认对话框
    wx.showModal({
      title: '删除知识库',
      content: `确定要删除「${selectedFolderName}」吗？\n删除后，其中的会议将移至「录音文件」`,
      confirmText: '删除',
      cancelText: '取消',
      confirmColor: '#FF3B30',
      success: (res) => {
        if (res.confirm) {
          // 执行删除
          this.deleteFolderRequest(selectedFolderId)
        }
      }
    })
  },

  // 删除知识库请求
  async deleteFolderRequest(folderId) {
    try {
      showLoading('删除中...')
      await API.deleteFolder(folderId)

      // 重新加载知识库列表
      await this.loadFolderList()

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
    } catch (error) {
      console.error('删除失败:', error)
      hideLoading()
      showToast(error.message || '删除失败', 'error')
    }
  },

  // ========== 会议操作功能 ✨重构 ==========
  
  // 会议长按事件
  onMeetingLongPress(e) {
    const { id, title, folderId, folderName } = e.currentTarget.dataset
    console.log('=== onMeetingLongPress 触发 ===')
    console.log('dataset:', e.currentTarget.dataset)
    console.log('会议ID:', id)
    console.log('会议标题:', title)
    console.log('知识库ID:', folderId)
    console.log('知识库名称:', folderName)
    
    wx.vibrateShort() // 震动反馈
    
    // 保存当前会议信息
    this.setData({
      movingMeetingId: id,
      movingMeetingTitle: title || '会议',
      meetingCurrentFolderId: folderId || null,
      meetingCurrentFolderName: folderName || '录音文件'
    })
    
    console.log('已保存到 data:', {
      movingMeetingId: this.data.movingMeetingId,
      movingMeetingTitle: this.data.movingMeetingTitle
    })
    
    // 显示微信原生 ActionSheet
    wx.showActionSheet({
      itemList: ['重命名', '复制到', '移动到', '删除'],
      success: (res) => {
        const tapIndex = res.tapIndex
        switch (tapIndex) {
          case 0:
            this.handleRenameMeeting()
            break
          case 1:
            this.handleCopyMeeting()
            break
          case 2:
            this.handleMoveMeeting()
            break
          case 3:
            this.handleDeleteMeeting()
            break
        }
      }
    })
  },

  // 1. 重命名会议
  handleRenameMeeting() {
    const { movingMeetingId, movingMeetingTitle } = this.data
    
    wx.showModal({
      title: '重命名会议',
      placeholderText: '请输入新标题',
      editable: true,
      content: movingMeetingTitle,
      confirmText: '确认',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          const newTitle = (res.content || '').trim()
          
          if (!newTitle) {
            showToast('请输入会议标题', 'error')
            return
          }
          
          if (newTitle === movingMeetingTitle) {
            showToast('标题未改变', 'none')
            return
          }
          
          // 执行重命名
          this.renameMeetingRequest(movingMeetingId, newTitle)
        }
      }
    })
  },

  // 重命名会议请求
  async renameMeetingRequest(meetingId, newTitle) {
    try {
      showLoading('重命名中...')
      await API.updateMeeting(meetingId, { title: newTitle })

      // 重新加载会议列表
      await this.loadMeetingList(true)

      hideLoading()
      showToast('重命名成功', 'success')
    } catch (error) {
      console.error('重命名失败:', error)
      hideLoading()
      showToast(error.message || '重命名失败', 'error')
    }
  },

  // 2. 复制会议到其他知识库
  handleCopyMeeting() {
    console.log('handleCopyMeeting 被调用')
    this.setData({
      showFolderSelector: true,
      folderSelectorAction: 'copy',
      selectedTargetFolderId: this.data.meetingCurrentFolderId
    })
  },

  // 3. 移动会议到其他知识库
  handleMoveMeeting() {
    console.log('handleMoveMeeting 被调用')
    this.setData({
      showFolderSelector: true,
      folderSelectorAction: 'move',
      selectedTargetFolderId: this.data.meetingCurrentFolderId
    })
  },

  // 隐藏知识库选择器
  hideFolderSelectorModal() {
    this.setData({ showFolderSelector: false })
  },

  // 选择目标知识库
  selectTargetFolder(e) {
    const folderId = e.currentTarget.dataset.id
    this.setData({ selectedTargetFolderId: folderId })
  },

  // 确认复制或移动
  confirmFolderAction() {
    const { folderSelectorAction, selectedTargetFolderId, folders, movingMeetingId } = this.data
    
    // 获取目标知识库名称
    let targetFolderName = '录音文件'
    if (selectedTargetFolderId !== null) {
      const targetFolder = folders.find(f => f.id === selectedTargetFolderId)
      targetFolderName = targetFolder ? targetFolder.name : '知识库'
    }
    
    console.log('确认操作:', folderSelectorAction, '目标:', targetFolderName)
    
    // 关闭选择器
    this.setData({ showFolderSelector: false })
    
    // 执行操作
    if (folderSelectorAction === 'copy') {
      this.copyMeetingRequest(movingMeetingId, selectedTargetFolderId, targetFolderName)
    } else {
      this.moveMeetingRequest(movingMeetingId, selectedTargetFolderId, targetFolderName)
    }
  },

  // 复制会议请求
  async copyMeetingRequest(meetingId, targetFolderId, targetFolderName) {
    try {
      console.log('=== 开始复制会议 ===')
      console.log('会议ID:', meetingId)
      console.log('目标知识库ID:', targetFolderId)
      console.log('目标知识库名称:', targetFolderName)
      
      showLoading('复制中...')
      
      // 调用复制 API
      const result = await API.copyMeeting(meetingId, { folder_id: targetFolderId })
      console.log('API 返回结果:', result)

      // 重新加载知识库列表
      await this.loadFolderList()

      hideLoading()
      showToast(`已复制到「${targetFolderName}」`, 'success')
      console.log('=== 复制成功 ===')
      
      // 跳转到目标知识库
      this.switchToFolder(targetFolderId, targetFolderName)
    } catch (error) {
      console.error('复制失败:', error)
      hideLoading()
      showToast(error.message || '复制失败', 'error')
    }
  },

  // 移动会议请求
  async moveMeetingRequest(meetingId, targetFolderId, targetFolderName) {
    try {
      console.log('=== 开始移动会议 ===')
      console.log('会议ID:', meetingId)
      console.log('目标知识库ID:', targetFolderId)
      console.log('目标知识库名称:', targetFolderName)
      
      showLoading('移动中...')
      
      const updateData = { folder_id: targetFolderId }
      console.log('更新数据:', updateData)
      
      const result = await API.updateMeeting(meetingId, updateData)
      console.log('API 返回结果:', result)

      // 重新加载知识库列表
      await this.loadFolderList()

      hideLoading()
      showToast(`已移动到「${targetFolderName}」`, 'success')
      console.log('=== 移动成功 ===')
      
      // 跳转到目标知识库
      this.switchToFolder(targetFolderId, targetFolderName)
    } catch (error) {
      console.error('移动失败:', error)
      hideLoading()
      showToast(error.message || '移动失败', 'error')
    }
  },

  // 切换到指定知识库
  switchToFolder(folderId, folderName) {
    console.log('切换到知识库:', folderName, '(ID:', folderId, ')')
    
    // 更新当前知识库
    this.setData({
      currentFolderId: folderId === null ? 'uncategorized' : folderId,
      currentFolderName: folderName || '录音文件'
    })
    
    // 重新加载会议列表
    this.loadMeetingList(true)
  },

  // 4. 删除会议
  handleDeleteMeeting() {
    const { movingMeetingId, movingMeetingTitle } = this.data
    
    wx.showModal({
      title: '删除会议',
      content: `确定要删除「${movingMeetingTitle}」吗？\n删除后无法恢复`,
      confirmText: '删除',
      cancelText: '取消',
      confirmColor: '#FF3B30',
      success: (res) => {
        if (res.confirm) {
          this.deleteMeetingRequest(movingMeetingId)
        }
      }
    })
  },

  // 删除会议请求
  async deleteMeetingRequest(meetingId) {
    try {
      showLoading('删除中...')
      await API.deleteMeeting(meetingId)

      // 重新加载知识库列表和会议列表
      await this.loadFolderList()
      await this.loadMeetingList(true)

      hideLoading()
      showToast('会议已删除', 'success')
    } catch (error) {
      console.error('删除失败:', error)
      hideLoading()
      showToast(error.message || '删除失败', 'error')
    }
  },

  // 阻止关闭
  preventClose() {
    // 空函数，用于阻止点击 Modal 内部关闭
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，用于阻止事件冒泡到遮罩层
  },

  // 阻止冒泡（用于 Modal）
  stopBubbling(e) {
    console.log('stopBubbling 被调用，阻止事件冒泡')
    // 空函数，catchtap 会自动阻止冒泡
  },

  /**
   * 阻止事件冒泡
   */
  preventDefault() {
    // 空函数，用于阻止滚动穿透
  }
})
