// app.js
const api = require('./utils/api')
const { STORAGE_KEYS } = require('./utils/config')
const { showError } = require('./utils/toast')

App({
  /**
   * 全局数据
   */
  globalData: {
    token: '',
    userInfo: null,
    userId: '',
    aiPollingTimers: {},  // 存储所有的 AI 轮询定时器
    uploadFile: null      // 临时存储待上传的文件信息
  },

  /**
   * 应用启动
   */
  onLaunch() {
    console.log('Cshine 小程序启动')
    
    // 检查登录状态，如果未登录则自动登录
    if (!this.checkLoginStatus()) {
      console.log('未登录，执行自动登录...')
      this.doLogin()
    }
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync(STORAGE_KEYS.TOKEN)
    const userInfo = wx.getStorageSync(STORAGE_KEYS.USER_INFO)
    const userId = wx.getStorageSync(STORAGE_KEYS.USER_ID)

    if (token && userId) {
      console.log('已登录，Token:', token.substring(0, 20) + '...')
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      this.globalData.userId = userId
      return true
    } else {
      console.log('未登录')
      return false
    }
  },

  /**
   * 执行登录
   */
  async doLogin() {
    try {
      console.log('开始微信登录...')

      // 1. 获取微信登录凭证
      const loginRes = await wx.login()
      const code = loginRes.code

      if (!code) {
        throw new Error('获取登录凭证失败')
      }

      console.log('获取到 code:', code.substring(0, 20) + '...')

      // 2. 获取用户信息（可选，如果需要昵称和头像）
      // 注意：新版本需要用户授权才能获取昵称头像
      let userInfo = {
        nickname: 'Cshine用户',
        avatar: ''
      }

      // 3. 调用后端登录接口
      const loginResult = await api.login(code, userInfo)
      
      console.log('登录成功:', loginResult)

      // 4. 保存登录信息
      wx.setStorageSync(STORAGE_KEYS.TOKEN, loginResult.token)
      wx.setStorageSync(STORAGE_KEYS.USER_ID, loginResult.user_id)
      wx.setStorageSync(STORAGE_KEYS.USER_INFO, userInfo)

      // 5. 更新全局数据
      this.globalData.token = loginResult.token
      this.globalData.userId = loginResult.user_id
      this.globalData.userInfo = userInfo

      return loginResult

    } catch (error) {
      console.error('登录失败:', error)
      showError('登录失败，请重试')
      throw error
    }
  },

  /**
   * 退出登录
   */
  logout() {
    console.log('退出登录')
    
    // 清除存储
    wx.removeStorageSync(STORAGE_KEYS.TOKEN)
    wx.removeStorageSync(STORAGE_KEYS.USER_ID)
    wx.removeStorageSync(STORAGE_KEYS.USER_INFO)
    
    // 清除全局数据
    this.globalData.token = ''
    this.globalData.userId = ''
    this.globalData.userInfo = null
  },

  /**
   * 确保已登录
   * 如果未登录则自动登录
   */
  async ensureLogin() {
    if (this.checkLoginStatus()) {
      return true
    }

    try {
      await this.doLogin()
      return true
    } catch (error) {
      return false
    }
  },

  /**
   * 全局 AI 状态轮询（不会被页面刷新打断）
   * @param {string} flashId 闪记ID
   * @param {function} onComplete 完成回调
   * @param {function} onError 错误回调
   */
  startAIPolling(flashId, onComplete, onError) {
    console.log('[全局轮询] 🌍 启动全局 AI 轮询，flash_id:', flashId)
    
    const MAX_ATTEMPTS = 90
    const POLL_INTERVAL = 2000
    let attempts = 0

    const poll = async () => {
      try {
        attempts++
        console.log(`[全局轮询 ${attempts}/${MAX_ATTEMPTS}] 🔍 查询 flash_id=${flashId}`)
        
        const result = await api.getAIStatus(flashId)
        console.log(`[全局轮询 ${attempts}] 📦 API 返回:`, JSON.stringify(result))
        
        const { status, content, summary, keywords, category } = result
        console.log(`[全局轮询 ${attempts}] 📊 AI 状态: ${status}`)

        if (status === 'completed') {
          console.log(`[全局轮询 ${attempts}] ✅✅✅ AI 处理完成！`)
          console.log(`[全局轮询] 转写内容:`, content)
          console.log(`[全局轮询] 分类:`, category)
          
          // 清除定时器
          this.stopAIPolling(flashId)
          
          // 调用完成回调
          if (onComplete) {
            onComplete({ status, content, summary, keywords, category })
          }
          
          // 显示提示
          wx.showToast({
            title: 'AI 分析完成！',
            icon: 'success',
            duration: 2000
          })
          
        } else if (status === 'failed') {
          console.error(`[全局轮询 ${attempts}] ❌ AI 处理失败:`, result.error)
          this.stopAIPolling(flashId)
          if (onError) {
            onError(result.error)
          }
          
        } else if (status === 'processing' || status === 'pending') {
          console.log(`[全局轮询 ${attempts}] ⏳ 状态: ${status}，继续等待...`)
          if (attempts < MAX_ATTEMPTS) {
            // 保存定时器 ID
            this.globalData.aiPollingTimers[flashId] = setTimeout(poll, POLL_INTERVAL)
          } else {
            console.warn('[全局轮询] ⏰ AI 处理超时')
            this.stopAIPolling(flashId)
          }
        }
      } catch (error) {
        console.error(`[全局轮询 ${attempts}] ❌ 轮询出错:`, error)
        this.stopAIPolling(flashId)
        if (onError) {
          onError(error)
        }
      }
    }

    // 立即开始轮询
    console.log('[全局轮询] ⏰ 0.5秒后开始第一次轮询...')
    this.globalData.aiPollingTimers[flashId] = setTimeout(poll, 500)
  },

  /**
   * 停止 AI 轮询
   */
  stopAIPolling(flashId) {
    console.log('[全局轮询] ⏹️ 停止轮询:', flashId)
    if (this.globalData.aiPollingTimers[flashId]) {
      clearTimeout(this.globalData.aiPollingTimers[flashId])
      delete this.globalData.aiPollingTimers[flashId]
    }
  }
})
