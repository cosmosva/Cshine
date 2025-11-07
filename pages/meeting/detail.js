/**
 * 会议纪要详情页
 */

const API = require('../../utils/api')
const { showToast, showLoading, hideLoading, showModal } = require('../../utils/toast')
const { formatDateTime } = require('../../utils/format')

Page({
  data: {
    meetingId: '',
    meeting: null,
    loading: true,
    
    // 音频播放状态
    audioContext: null,
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    
    // Tab 切换
    activeTab: 'summary',  // summary / keyPoints / actions / transcript
    tabs: [
      { id: 'summary', name: '摘要' },
      { id: 'keyPoints', name: '要点' },
      { id: 'actions', name: '行动项' },
      { id: 'transcript', name: '全文' }
    ]
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ meetingId: options.id })
      this.loadMeetingDetail()
    }
    
    // 创建音频上下文
    const audioContext = wx.createInnerAudioContext()
    audioContext.onPlay(() => {
      this.setData({ isPlaying: true })
    })
    audioContext.onPause(() => {
      this.setData({ isPlaying: false })
    })
    audioContext.onEnded(() => {
      this.setData({ isPlaying: false, currentTime: 0 })
    })
    audioContext.onTimeUpdate(() => {
      this.setData({
        currentTime: audioContext.currentTime,
        duration: audioContext.duration
      })
    })
    
    this.setData({ audioContext })
  },

  onUnload() {
    // 销毁音频上下文
    if (this.data.audioContext) {
      this.data.audioContext.destroy()
    }
  },

  /**
   * 加载会议详情
   */
  async loadMeetingDetail() {
    this.setData({ loading: true })
    
    try {
      const meeting = await API.getMeetingDetail(this.data.meetingId)
      console.log('会议详情（已解包）:', meeting)
      
      if (meeting) {
        this.setData({
          meeting: meeting,
          loading: false
        })
        
        // 设置音频地址
        if (meeting.audio_url && this.data.audioContext) {
          this.data.audioContext.src = meeting.audio_url
        }
      }
    } catch (error) {
      console.error('加载会议详情失败:', error)
      this.setData({ loading: false })
      showToast('加载失败', 'error')
    }
  },

  /**
   * 切换 Tab
   */
  switchTab(e) {
    const tabId = e.currentTarget.dataset.tab
    this.setData({ activeTab: tabId })
  },

  /**
   * 播放/暂停音频
   */
  toggleAudio() {
    if (!this.data.audioContext) return
    
    if (this.data.isPlaying) {
      this.data.audioContext.pause()
    } else {
      this.data.audioContext.play()
    }
  },

  /**
   * 删除会议
   */
  async deleteMeeting() {
    const res = await showModal(
      '确认删除',
      '确定要删除这条会议纪要吗？'
    )
    
    if (!res.confirm) return
    
    showLoading('删除中...')
    
    try {
      await API.deleteMeeting(this.data.meetingId)
      
      showToast('删除成功', 'success')
      
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } catch (error) {
      console.error('删除会议失败:', error)
      showToast('删除失败，请重试', 'error')
    } finally {
      hideLoading()
    }
  },

  /**
   * 分享会议
   */
  shareMeeting() {
    // TODO: 实现分享功能
    showToast('分享功能开发中...', 'none')
  },

  /**
   * 导出会议
   */
  exportMeeting() {
    // TODO: 实现导出功能
    showToast('导出功能开发中...', 'none')
  },

  /**
   * 显示操作菜单
   */
  showActionMenu() {
    wx.showActionSheet({
      itemList: ['分享', '导出', '删除'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.shareMeeting()
            break
          case 1:
            this.exportMeeting()
            break
          case 2:
            this.deleteMeeting()
            break
        }
      }
    })
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
    if (!seconds) return '00:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }
})

