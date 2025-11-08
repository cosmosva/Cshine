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
    console.log('选中文件夹ID:', folderId)
    
    // TODO: 后续实现业务逻辑
    // 1. 根据文件夹ID筛选会议列表
    // 2. 更新导航栏标题为文件夹名称
    // 3. 关闭抽屉
    
    showToast('选中文件夹: ' + folderId, 'success')
    this.closeDrawer()
  },

  /**
   * 阻止事件冒泡
   */
  preventDefault() {
    // 空函数，用于阻止滚动穿透
  }
})
