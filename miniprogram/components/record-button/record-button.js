// 录音按钮组件
const { vibrateShort } = require('../../utils/toast')
const { formatDuration } = require('../../utils/format')

Component({
  properties: {
    // 最大录音时长（秒）
    maxDuration: {
      type: Number,
      value: 300 // 默认5分钟
    }
  },

  data: {
    isRecording: false,      // 是否正在录音
    isCanceling: false,      // 是否处于取消状态
    recordingTime: '0:00',   // 录音时长显示
    startY: 0,               // 触摸起始Y坐标
    recordTimer: null,       // 录音计时器
    recordSeconds: 0,        // 录音秒数
    startTime: 0             // 录音开始时间戳
  },

  lifetimes: {
    attached() {
      // 组件加载时初始化录音管理器（只初始化一次）
      console.log('[录音组件] 组件加载，初始化录音管理器')
      this.initRecorderManager()
    },
    
    detached() {
      console.log('[录音组件] 组件销毁，清理资源')
      // 组件销毁时清理
      this.stopRecording()
      
      // 移除事件监听器
      if (this.recorderManager) {
        this.recorderManager.onStart(() => {})
        this.recorderManager.onStop(() => {})
        this.recorderManager.onError(() => {})
      }
    }
  },

  methods: {
    /**
     * 初始化录音管理器（组件生命周期内只调用一次）
     */
    initRecorderManager() {
      console.log('[录音组件] 初始化录音管理器...')
      
      // 如果已经初始化过，不要重复初始化
      if (this.recorderManager && this._listenersInitialized) {
        console.log('[录音组件] 录音管理器已初始化，跳过')
        return
      }
      
      // 获取全局唯一的录音管理器实例
      const recorderManager = wx.getRecorderManager()
      
      // 保存实例
      this.recorderManager = recorderManager
      
      // 绑定事件监听器（只绑定一次）
      recorderManager.onStart(() => {
        console.log('[录音组件] 📢 录音开始')
      })
      
      recorderManager.onStop((res) => {
        console.log('[录音组件] 📢 录音停止事件触发')
        console.log('[录音组件] 录音文件路径:', res.tempFilePath)
        console.log('[录音组件] 录音时长(ms):', res.duration)
        console.log('[录音组件] 文件大小(bytes):', res.fileSize)
        
        // 检查实际录音时长（使用微信返回的真实时长）
        const actualDuration = Math.floor(res.duration / 1000) // 转换为秒
        
        // 开发测试：降低最小时长要求到0.3秒
        // 生产环境可以改为1秒
        if (actualDuration < 0.3) {
          console.log('[录音组件] ⚠️ 录音时间太短')
          this.triggerEvent('recorderror', { 
            error: { message: '录音时间太短，请长按至少1秒' } 
          })
          return
        }
        
        console.log('[录音组件] ✅ 触发 recordend 事件')
        // 触发录音完成事件
        this.triggerEvent('recordend', {
          tempFilePath: res.tempFilePath,
          duration: actualDuration,
          fileSize: res.fileSize
        })
      })
      
      recorderManager.onError((err) => {
        console.error('[录音组件] ❌ 录音失败:', err)
        this.triggerEvent('recorderror', { error: err })
        this.stopRecording()
      })
      
      // 标记监听器已初始化
      this._listenersInitialized = true
      console.log('[录音组件] ✅ 录音管理器初始化完成')
    },
    
    /**
     * 触摸开始 - 开始录音
     */
    onTouchStart(e) {
      // 防止重复触发
      if (this.data.isRecording) {
        console.log('录音已在进行中，忽略重复触发')
        return
      }

      console.log('开始录音')

      // 震动反馈
      vibrateShort('medium')

      // 记录开始时间戳和触摸位置
      const startTime = Date.now()
      this.setData({
        startY: e.touches[0].clientY,
        isRecording: true,
        isCanceling: false,
        recordSeconds: 0,
        recordingTime: '0:00',
        startTime: startTime
      })

      // 开始录音
      this.startRecording()

      // 启动计时器
      this.startTimer()

      // 触发开始录音事件
      this.triggerEvent('recordstart')
    },

    /**
     * 触摸移动 - 判断是否取消
     */
    onTouchMove(e) {
      const currentY = e.touches[0].clientY
      const deltaY = this.data.startY - currentY
      
      // 上滑超过60px进入取消状态
      const isCanceling = deltaY > 60
      
      if (isCanceling !== this.data.isCanceling) {
        this.setData({ isCanceling })
        vibrateShort('light')
      }
    },

    /**
     * 触摸结束 - 完成或取消录音
     */
    onTouchEnd(e) {
      console.log('触摸结束')
      
      if (this.data.isCanceling) {
        // 取消录音
        this.cancelRecording()
      } else {
        // 完成录音
        this.finishRecording()
      }
    },

    /**
     * 触摸取消 - 取消录音
     */
    onTouchCancel(e) {
      console.log('触摸取消')
      this.cancelRecording()
    },

    /**
     * 开始录音
     */
    startRecording() {
      if (!this.recorderManager) {
        console.error('录音管理器未初始化')
        this.initRecorderManager()
      }
      
      // 使用已初始化的录音管理器开始录音
      this.recorderManager.start({
        duration: this.data.maxDuration * 1000,
        sampleRate: 16000,
        numberOfChannels: 1,
        encodeBitRate: 48000,
        format: 'mp3'
      })
    },

    /**
     * 启动计时器（基于时间戳计算，更准确）
     */
    startTimer() {
      // 每100ms更新一次显示，更流畅
      this.data.recordTimer = setInterval(() => {
        const now = Date.now()
        const elapsed = now - this.data.startTime
        const seconds = Math.floor(elapsed / 1000)
        
        this.setData({
          recordSeconds: seconds,
          recordingTime: formatDuration(seconds)
        })
        
        // 达到最大时长自动停止
        if (seconds >= this.data.maxDuration) {
          this.finishRecording()
        }
      }, 100) // 100ms 更新一次，显示更流畅
    },

    /**
     * 停止计时器
     */
    stopTimer() {
      if (this.data.recordTimer) {
        clearInterval(this.data.recordTimer)
        this.setData({ recordTimer: null })
      }
    },

    /**
     * 完成录音
     */
    finishRecording() {
      const seconds = Math.floor((Date.now() - this.data.startTime) / 1000)
      console.log('[录音组件] 🎤 完成录音，实际时长:', seconds, '秒')
      
      // 停止录音（onStop 监听器已在 initRecorderManager 中绑定）
      if (this.recorderManager) {
        this.recorderManager.stop()
      }
      
      // 重置状态
      this.stopRecording()
      
      // 震动反馈
      vibrateShort('light')
    },

    /**
     * 取消录音
     */
    cancelRecording() {
      console.log('取消录音')
      
      // 停止录音
      if (this.recorderManager) {
        this.recorderManager.stop()
      }
      
      // 重置状态
      this.stopRecording()
      
      // 触发取消事件
      this.triggerEvent('recordcancel')
      
      // 震动反馈
      vibrateShort('light')
    },

    /**
     * 停止录音（清理状态）
     */
    stopRecording() {
      this.stopTimer()
      this.setData({
        isRecording: false,
        isCanceling: false,
        recordSeconds: 0,
        recordingTime: '0:00',
        startTime: 0
      })
    }
  }
})

