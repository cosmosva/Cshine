// 闪记详情页
const api = require('../../utils/api')
const { showSuccess, showError, showLoading, hideLoading } = require('../../utils/toast')
const { formatTime, formatDuration } = require('../../utils/format')

Page({
  data: {
    flashId: '',
    flash: null,
    isLoading: true,
    
    // 音频播放相关
    isPlaying: false,
    playProgress: 0,
    currentTime: 0,
    currentTimeText: '0:00',
    durationText: '0:00',
  },

  /**
   * 生命周期 - 页面加载
   */
  onLoad(options) {
    const { id } = options
    if (!id) {
      showError('闪记不存在')
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
      return
    }

    this.setData({ flashId: id })
    this.loadFlashDetail()
    this.initAudioPlayer()
  },

  /**
   * 生命周期 - 页面卸载
   */
  onUnload() {
    // 停止音频播放
    if (this.audioContext) {
      this.audioContext.stop()
      this.audioContext.destroy()
    }
  },

  /**
   * 返回上一页
   */
  onBack() {
    wx.navigateBack()
  },

  /**
   * 加载闪记详情
   */
  async loadFlashDetail() {
    try {
      this.setData({ isLoading: true })
      
      const flash = await api.getFlashDetail(this.data.flashId)
      console.log('闪记详情:', flash)
      
      // 格式化时间
      flash.created_at = formatTime(new Date(flash.created_at))
      
      // 如果有音频，格式化时长
      if (flash.audio_duration) {
        this.setData({
          durationText: formatDuration(flash.audio_duration)
        })
      }
      
      this.setData({
        flash,
        isLoading: false
      })
    } catch (error) {
      console.error('加载详情失败:', error)
      showError('加载失败')
      this.setData({ isLoading: false })
      
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  /**
   * 初始化音频播放器
   */
  initAudioPlayer() {
    this.audioContext = wx.createInnerAudioContext()
    
    // 播放开始
    this.audioContext.onPlay(() => {
      console.log('音频开始播放')
      this.setData({ isPlaying: true })
      this.startProgressUpdate()
    })
    
    // 播放暂停
    this.audioContext.onPause(() => {
      console.log('音频暂停')
      this.setData({ isPlaying: false })
      this.stopProgressUpdate()
    })
    
    // 播放结束
    this.audioContext.onEnded(() => {
      console.log('音频播放结束')
      this.setData({
        isPlaying: false,
        playProgress: 0,
        currentTime: 0,
        currentTimeText: '0:00'
      })
      this.stopProgressUpdate()
    })
    
    // 播放错误
    this.audioContext.onError((err) => {
      console.error('音频播放错误:', err)
      showError('播放失败')
      this.setData({ isPlaying: false })
      this.stopProgressUpdate()
    })
  },

  /**
   * 切换播放/暂停
   */
  togglePlay() {
    if (!this.data.flash.audio_url) {
      showError('没有音频')
      return
    }

    if (this.data.isPlaying) {
      this.audioContext.pause()
    } else {
      // 设置音频源
      if (this.audioContext.src !== this.data.flash.audio_url) {
        this.audioContext.src = this.data.flash.audio_url
      }
      this.audioContext.play()
    }
  },

  /**
   * 开始更新播放进度
   */
  startProgressUpdate() {
    this.progressTimer = setInterval(() => {
      const currentTime = this.audioContext.currentTime
      const duration = this.audioContext.duration || this.data.flash.audio_duration
      
      if (duration > 0) {
        const progress = (currentTime / duration) * 100
        this.setData({
          playProgress: Math.min(progress, 100),
          currentTime: currentTime,
          currentTimeText: formatDuration(Math.floor(currentTime))
        })
      }
    }, 500)
  },

  /**
   * 停止更新播放进度
   */
  stopProgressUpdate() {
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
      this.progressTimer = null
    }
  },

  /**
   * 编辑闪记
   */
  onEdit() {
    wx.navigateTo({
      url: `/pages/edit/edit?id=${this.data.flashId}`
    })
  },

  /**
   * 切换收藏状态
   */
  async onToggleFavorite() {
    try {
      await api.toggleFavorite(this.data.flashId)
      
      const isFavorite = !this.data.flash.is_favorite
      this.setData({
        'flash.is_favorite': isFavorite
      })
      
      showSuccess(isFavorite ? '已收藏' : '已取消收藏')
    } catch (error) {
      console.error('收藏失败:', error)
      showError('操作失败')
    }
  },

  /**
   * 删除闪记
   */
  onDelete() {
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复，确定要删除这条闪记吗？',
      confirmText: '删除',
      confirmColor: '#FF4D4F',
      success: async (res) => {
        if (res.confirm) {
          await this.deleteFlash()
        }
      }
    })
  },

  /**
   * 执行删除
   */
  async deleteFlash() {
    try {
      showLoading('删除中...')
      
      await api.deleteFlash(this.data.flashId)
      
      hideLoading()
      showSuccess('删除成功')
      
      // 返回上一页并刷新
      setTimeout(() => {
        wx.navigateBack()
      }, 1000)
    } catch (error) {
      console.error('删除失败:', error)
      hideLoading()
      showError('删除失败')
    }
  }
})

