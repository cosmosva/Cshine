/**
 * 会议纪要列表页
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
    hasMore: true,
    
    // 筛选器
    statusFilter: 'all',  // all / pending / processing / completed / failed
    statusOptions: [
      { label: '全部', value: 'all' },
      { label: '处理中', value: 'processing' },
      { label: '已完成', value: 'completed' },
      { label: '失败', value: 'failed' }
    ],
    
    // 状态文案映射
    statusTextMap: {
      'pending': '等待处理',
      'processing': '处理中',
      'completed': '已完成',
      'failed': '处理失败'
    },
    
    // 状态颜色映射
    statusColorMap: {
      'pending': '#999',
      'processing': '#4A6FE8',
      'completed': '#34C759',
      'failed': '#FF3B30'
    }
  },

  onLoad() {
    this.loadMeetingList()
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
        page_size: this.data.pageSize
      }
      
      // 添加状态筛选
      if (this.data.statusFilter !== 'all') {
        params.status = this.data.statusFilter
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
  onPullDownRefresh() {
    this.loadMeetingList(true).then(() => {
      wx.stopPullDownRefresh()
    })
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    this.loadMeetingList()
  },

  /**
   * 切换状态筛选
   */
  onStatusChange(e) {
    const status = e.currentTarget.dataset.status
    if (status === this.data.statusFilter) return
    
    this.setData({ statusFilter: status })
    this.loadMeetingList(true)
  },

  /**
   * 跳转到上传页
   */
  goToUpload() {
    wx.navigateTo({
      url: '/pages/meeting/upload'
    })
  },

  /**
   * 查看会议详情
   */
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
  },

  /**
   * 删除会议
   */
  async deleteMeeting(e) {
    const meetingId = e.currentTarget.dataset.id
    
    // 确认对话框
    const res = await wx.showModal({
      title: '确认删除',
      content: '确定要删除这条会议纪要吗？',
      confirmText: '删除',
      confirmColor: '#FF3B30'
    })
    
    if (!res.confirm) return
    
    showLoading('删除中...')
    
    try {
      await API.deleteMeeting(meetingId)
      
      showToast('删除成功', 'success')
      
      // 从列表中移除
      const newList = this.data.meetingList.filter(item => item.id !== meetingId)
      this.setData({
        meetingList: newList,
        total: this.data.total - 1
      })
    } catch (error) {
      console.error('删除会议失败:', error)
      showToast('删除失败，请重试', 'error')
    } finally {
      hideLoading()
    }
  },

  /**
   * 格式化时间
   */
  formatTime(dateStr) {
    return formatDateTime(dateStr)
  },

  /**
   * 格式化时长
   */
  formatDuration(seconds) {
    if (!seconds) return '未知'
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return `${hours}小时${mins}分钟`
    }
    return `${minutes}分${secs}秒`
  }
})

