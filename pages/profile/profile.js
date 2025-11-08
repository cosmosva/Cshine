// pages/profile/profile.js
const { showToast } = require('../../utils/toast')

Page({
  data: {
    userInfo: null,
    isLogin: false,
    stats: {
      flashCount: 0,
      meetingCount: 0,
      todayCount: 0,
      totalDuration: 0
    }
  },

  onLoad() {
    this.checkLoginStatus()
  },

  onShow() {
    // 每次显示时刷新统计数据
    if (this.data.isLogin) {
      this.loadUserStats()
    }
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.setData({
        isLogin: true,
        userInfo: userInfo
      })
      this.loadUserStats()
    }
  },

  /**
   * 加载用户统计数据
   */
  async loadUserStats() {
    try {
      // TODO: 调用后端 API 获取统计数据
      // const stats = await API.getUserStats()
      
      // 临时使用本地数据
      const flashList = wx.getStorageSync('flashList') || []
      const meetingList = wx.getStorageSync('meetingList') || []
      
      // 计算今日数据
      const today = new Date().toDateString()
      const todayFlash = flashList.filter(item => {
        return new Date(item.created_at).toDateString() === today
      })
      
      this.setData({
        'stats.flashCount': flashList.length,
        'stats.meetingCount': meetingList.length,
        'stats.todayCount': todayFlash.length,
        'stats.totalDuration': flashList.reduce((sum, item) => sum + (item.audio_duration || 0), 0)
      })
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  },

  /**
   * 登录
   */
  handleLogin() {
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (res) => {
        console.log('获取用户信息成功:', res)
        const userInfo = res.userInfo
        
        // TODO: 调用后端登录接口
        // 临时保存到本地
        wx.setStorageSync('userInfo', userInfo)
        
        this.setData({
          isLogin: true,
          userInfo: userInfo
        })
        
        this.loadUserStats()
        showToast('登录成功', 'success')
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err)
        showToast('登录失败', 'error')
      }
    })
  },

  /**
   * 退出登录
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          
          this.setData({
            isLogin: false,
            userInfo: null,
            stats: {
              flashCount: 0,
              meetingCount: 0,
              todayCount: 0,
              totalDuration: 0
            }
          })
          
          showToast('已退出登录', 'success')
        }
      }
    })
  },

  /**
   * 格式化时长
   */
  formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (hours > 0) {
      return `${hours}小时${minutes}分钟`
    }
    return `${minutes}分钟`
  },

  /**
   * 跳转到设置页
   */
  goToSettings() {
    showToast('设置功能开发中', 'none')
  },

  /**
   * 跳转到关于页
   */
  goToAbout() {
    showToast('关于页面开发中', 'none')
  },

  /**
   * 跳转到帮助页
   */
  goToHelp() {
    showToast('帮助中心开发中', 'none')
  },

  /**
   * 数据导出
   */
  handleExport() {
    showToast('数据导出功能开发中', 'none')
  },

  /**
   * 清除缓存
   */
  handleClearCache() {
    wx.showModal({
      title: '清除缓存',
      content: '确定要清除本地缓存吗？不会影响云端数据',
      success: (res) => {
        if (res.confirm) {
          // 清除非关键数据
          wx.removeStorageSync('flashList')
          wx.removeStorageSync('meetingList')
          
          showToast('缓存已清除', 'success')
          this.loadUserStats()
        }
      }
    })
  }
})

