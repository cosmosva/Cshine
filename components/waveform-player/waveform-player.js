/**
 * 音频波形播放器组件
 */

const API = require('../../utils/api')

Component({
  properties: {
    // 音频URL
    audioUrl: {
      type: String,
      value: ''
    },
    // 音频时长（秒）
    duration: {
      type: Number,
      value: 0
    },
    // 会议ID（用于获取波形数据）
    meetingId: {
      type: String,
      value: ''
    }
  },

  data: {
    // 播放状态
    isPlaying: false,
    currentTime: 0,
    
    // 倍速选项
    playbackRate: 1.0,
    speedOptions: [0.5, 1.0, 1.5, 2.0],
    
    // 波形数据
    waveformData: [],
    loading: true,
    
    // Canvas相关
    canvasWidth: 0,
    canvasHeight: 0,
    pixelRatio: 1
  },

  lifetimes: {
    attached() {
      // 组件加载时初始化
      this.initAudioContext()
      this.initCanvas()
      this.loadWaveform()
    },
    
    detached() {
      // 组件卸载时清理
      if (this.audioContext) {
        this.audioContext.destroy()
      }
      if (this.animationFrame) {
        cancelAnimationFrame(this.animationFrame)
      }
    }
  },

  methods: {
    /**
     * 初始化音频上下文
     */
    initAudioContext() {
      const audioContext = wx.createInnerAudioContext()
      
      audioContext.src = this.properties.audioUrl
      
      // 监听播放事件
      audioContext.onPlay(() => {
        this.setData({ isPlaying: true })
        this.startAnimation()
      })
      
      audioContext.onPause(() => {
        this.setData({ isPlaying: false })
        this.stopAnimation()
      })
      
      audioContext.onEnded(() => {
        this.setData({ 
          isPlaying: false,
          currentTime: 0
        })
        this.stopAnimation()
        this.drawWaveform()
      })
      
      audioContext.onTimeUpdate(() => {
        this.setData({
          currentTime: audioContext.currentTime
        })
      })
      
      audioContext.onError((err) => {
        console.error('音频播放错误:', err)
        wx.showToast({
          title: '播放失败',
          icon: 'none'
        })
      })
      
      this.audioContext = audioContext
    },

    /**
     * 初始化Canvas
     */
    initCanvas() {
      const query = this.createSelectorQuery()
      query.select('.waveform-canvas')
        .boundingClientRect((rect) => {
          if (rect) {
            const pixelRatio = wx.getSystemInfoSync().pixelRatio || 1
            
            this.setData({
              canvasWidth: rect.width,
              canvasHeight: rect.height,
              pixelRatio: pixelRatio
            })
            
            // 获取Canvas上下文
            this.canvasContext = wx.createCanvasContext('waveformCanvas', this)
          }
        })
        .exec()
    },

    /**
     * 加载波形数据
     */
    async loadWaveform() {
      if (!this.properties.meetingId) {
        console.warn('未提供meetingId，无法加载波形')
        this.setData({ loading: false })
        return
      }
      
      try {
        this.setData({ loading: true })
        
        const response = await API.getMeetingWaveform(this.properties.meetingId)
        
        if (response && response.waveform) {
          this.setData({
            waveformData: response.waveform,
            loading: false
          })
          
          // 延迟绘制，确保Canvas已初始化
          setTimeout(() => {
            this.drawWaveform()
          }, 300)
        }
      } catch (error) {
        console.error('加载波形数据失败:', error)
        this.setData({ loading: false })
        wx.showToast({
          title: '波形加载失败',
          icon: 'none'
        })
      }
    },

    /**
     * 绘制波形
     */
    drawWaveform() {
      if (!this.canvasContext || !this.data.waveformData.length) {
        return
      }
      
      const ctx = this.canvasContext
      const { canvasWidth, canvasHeight, waveformData, currentTime } = this.data
      const duration = this.properties.duration || this.audioContext?.duration || 1
      
      // 清空画布
      ctx.clearRect(0, 0, canvasWidth, canvasHeight)
      
      // 计算进度
      const progress = currentTime / duration
      const progressX = canvasWidth * progress
      
      // 绘制参数
      const barWidth = canvasWidth / waveformData.length
      const centerY = canvasHeight / 2
      const maxBarHeight = canvasHeight * 0.8
      
      // 绘制波形
      waveformData.forEach((amplitude, index) => {
        const x = index * barWidth
        const barHeight = amplitude * maxBarHeight / 2
        
        // 判断是否已播放
        const isPlayed = x < progressX
        
        // 设置颜色
        ctx.setFillStyle(isPlayed ? '#FF0000' : '#333333')
        
        // 绘制上半部分
        ctx.fillRect(x, centerY - barHeight, barWidth - 1, barHeight)
        
        // 绘制下半部分（镜像）
        ctx.fillRect(x, centerY, barWidth - 1, barHeight)
      })
      
      // 绘制进度指示线
      ctx.setStrokeStyle('#FF0000')
      ctx.setLineWidth(2)
      ctx.beginPath()
      ctx.moveTo(progressX, 0)
      ctx.lineTo(progressX, canvasHeight)
      ctx.stroke()
      
      ctx.draw()
    },

    /**
     * 开始动画（实时更新波形）
     */
    startAnimation() {
      const animate = () => {
        this.drawWaveform()
        if (this.data.isPlaying) {
          this.animationFrame = requestAnimationFrame(animate)
        }
      }
      animate()
    },

    /**
     * 停止动画
     */
    stopAnimation() {
      if (this.animationFrame) {
        cancelAnimationFrame(this.animationFrame)
        this.animationFrame = null
      }
    },

    /**
     * 播放/暂停
     */
    togglePlay() {
      if (!this.audioContext) return
      
      if (this.data.isPlaying) {
        this.audioContext.pause()
      } else {
        this.audioContext.play()
      }
    },

    /**
     * 切换倍速
     */
    changeSpeed() {
      const { playbackRate, speedOptions } = this.data
      const currentIndex = speedOptions.indexOf(playbackRate)
      const nextIndex = (currentIndex + 1) % speedOptions.length
      const newRate = speedOptions[nextIndex]
      
      this.setData({ playbackRate: newRate })
      
      if (this.audioContext) {
        this.audioContext.playbackRate = newRate
      }
      
      wx.showToast({
        title: `${newRate}x`,
        icon: 'none',
        duration: 1000
      })
    },

    /**
     * 后退15秒
     */
    seekBackward() {
      if (!this.audioContext) return
      
      const newTime = Math.max(0, this.audioContext.currentTime - 15)
      this.audioContext.seek(newTime)
      
      this.setData({ currentTime: newTime })
      this.drawWaveform()
    },

    /**
     * 前进15秒
     */
    seekForward() {
      if (!this.audioContext) return
      
      const duration = this.properties.duration || this.audioContext.duration
      const newTime = Math.min(duration, this.audioContext.currentTime + 15)
      this.audioContext.seek(newTime)
      
      this.setData({ currentTime: newTime })
      this.drawWaveform()
    },

    /**
     * 格式化时间
     */
    formatTime(seconds) {
      if (!seconds || isNaN(seconds)) return '00:00'
      
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      
      return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
    }
  }
})

