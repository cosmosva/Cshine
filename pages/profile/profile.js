// pages/profile/profile.js
const { showToast } = require('../../utils/toast')
const API = require('../../utils/api')

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
   * 登录（完整流程）
   */
  async handleLogin() {
    try {
      // 显示加载状态
      wx.showLoading({ title: '登录中...', mask: true })
      
      // 1. 获取微信登录凭证（code）
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        })
      })
      
      if (!loginRes.code) {
        throw new Error('获取微信登录凭证失败')
      }
      
      console.log('微信登录 code:', loginRes.code)
      
      // 2. 获取用户信息
      const profileRes = await new Promise((resolve, reject) => {
        wx.getUserProfile({
          desc: '用于完善用户资料',
          success: resolve,
          fail: reject
        })
      })
      
      const userInfo = profileRes.userInfo
      console.log('用户信息:', userInfo)
      
      // 3. 调用后端登录接口
      const loginData = await API.login(loginRes.code, {
        nickname: userInfo.nickName,
        avatar: userInfo.avatarUrl
      })
      
      console.log('后端登录成功:', loginData)
      
      // 4. 保存 Token 和用户信息
      wx.setStorageSync('token', loginData.token)
      wx.setStorageSync('userInfo', {
        id: loginData.user_id,
        nickname: userInfo.nickName,
        avatar: userInfo.avatarUrl,
        isNewUser: loginData.is_new_user
      })
      
      // 5. 更新页面状态
      this.setData({
        isLogin: true,
        userInfo: {
          id: loginData.user_id,
          nickname: userInfo.nickName,
          avatar: userInfo.avatarUrl
        }
      })
      
      wx.hideLoading()
      
      // 6. 加载统计数据
      this.loadUserStats()
      
      // 7. 提示用户
      if (loginData.is_new_user) {
        showToast('欢迎使用 Cshine！', 'success')
      } else {
        showToast('登录成功', 'success')
      }
      
    } catch (error) {
      wx.hideLoading()
      console.error('登录失败:', error)
      
      let errorMsg = '登录失败，请重试'
      if (error.errMsg && error.errMsg.includes('getUserProfile:fail auth deny')) {
        errorMsg = '您取消了授权'
      } else if (error.detail) {
        errorMsg = error.detail
      }
      
      showToast(errorMsg, 'error')
    }
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
          // 清除所有登录相关数据
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          
          // 重置页面状态
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
          
          console.log('用户已退出登录')
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

