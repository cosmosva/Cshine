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
    activeTab: 'summary',  // summary / transcript / mindmap
    tabs: [
      { id: 'summary', name: '总结' },
      { id: 'transcript', name: '转录' },
      { id: 'mindmap', name: '思维导图' }
    ],
    
    // 说话人映射
    speakerMap: {},  // { "说话人1": "张三", "说话人2": "李四" }
    
    // 联系人列表（用于标注）
    contacts: [],
    
    // 标注弹窗
    showSpeakerModal: false,
    currentSpeaker: null
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ meetingId: options.id })
      this.loadMeetingDetail()
      this.loadSpeakerMap()
      this.loadContacts()
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

  onHide() {
    // 页面隐藏时暂停音频
    if (this.data.audioContext && this.data.isPlaying) {
      this.data.audioContext.pause()
    }
  },

  onUnload() {
    // 销毁音频上下文
    if (this.data.audioContext) {
      this.data.audioContext.pause()
      this.data.audioContext.destroy()
    }
    
    // 清除状态轮询定时器
    if (this.statusTimer) {
      clearInterval(this.statusTimer)
      this.statusTimer = null
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
  },

  /**
   * 加载说话人映射
   */
  async loadSpeakerMap() {
    try {
      const response = await API.getMeetingSpeakers(this.data.meetingId)
      console.log('说话人映射:', response)
      
      const speakerMap = {}
      if (response.items) {
        response.items.forEach(item => {
          speakerMap[item.speaker_id] = item.display_name
        })
      }
      
      this.setData({ speakerMap })
    } catch (error) {
      console.error('加载说话人映射失败:', error)
    }
  },

  /**
   * 加载联系人列表
   */
  async loadContacts() {
    try {
      const response = await API.getContacts()
      this.setData({ contacts: response.items || [] })
    } catch (error) {
      console.error('加载联系人失败:', error)
    }
  },

  /**
   * 开始处理会议（立即生成）
   */
  async startProcessing() {
    const { meeting } = this.data
    if (!meeting || !meeting.id) return

    // 确认对话框
    const res = await showModal(
      '开始处理',
      '即将开始 AI 分析，生成会议摘要、转录和思维导图，大约需要几分钟时间。'
    )
    
    if (!res.confirm) return
    
    try {
      showLoading('启动处理中...')
      
      // 调用 reprocess 接口触发处理
      await API.reprocessMeeting(meeting.id)
      
      hideLoading()
      showToast('处理已启动', 'success')
      
      // 更新状态为 processing
      this.setData({
        'meeting.status': 'processing'
      })
      
      // 开始轮询状态
      this.startStatusPolling()
      
    } catch (error) {
      hideLoading()
      console.error('启动处理失败:', error)
      showToast('启动失败，请重试', 'error')
    }
  },

  /**
   * 开始状态轮询
   */
  startStatusPolling() {
    // 清除之前的定时器
    if (this.statusTimer) {
      clearInterval(this.statusTimer)
    }
    
    // 每 3 秒轮询一次
    this.statusTimer = setInterval(() => {
      this.checkProcessingStatus()
    }, 3000)
  },

  /**
   * 检查处理状态
   */
  async checkProcessingStatus() {
    const { meeting } = this.data
    if (!meeting || !meeting.id) return
    
    try {
      const status = await API.getMeetingStatus(meeting.id)
      console.log('会议状态:', status)
      
      // 如果状态变为 completed 或 failed，停止轮询并刷新详情
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(this.statusTimer)
        this.statusTimer = null
        
        // 刷新详情页
        this.loadMeetingDetail()
        
        if (status.status === 'completed') {
          showToast('处理完成', 'success')
        } else {
          showToast('处理失败，请重试', 'error')
        }
      }
      
    } catch (error) {
      console.error('检查状态失败:', error)
    }
  },

  /**
   * 重新处理会议
   */
  async reprocessMeeting() {
    const { meeting } = this.data
    if (!meeting || !meeting.id) return

    const res = await showModal(
      '重新处理',
      '确定要重新处理这个会议吗？这将重新生成摘要、思维导图等内容。'
    )
    
    if (!res.confirm) return
    
    try {
      showLoading('启动处理中...')
      await API.reprocessMeeting(meeting.id)
      hideLoading()
      showToast('处理已启动', 'success')
      
      // 更新状态为 processing
      this.setData({
        'meeting.status': 'processing'
      })
      
      // 开始轮询状态
      this.startStatusPolling()
      
    } catch (error) {
      hideLoading()
      console.error('重新处理失败:', error)
      showToast('启动失败，请重试', 'error')
    }
  },

  /**
   * 显示说话人标注弹窗
   */
  showSpeakerAnnotation(e) {
    const speakerId = e.currentTarget.dataset.speaker
    this.setData({
      showSpeakerModal: true,
      currentSpeaker: speakerId
    })
  },

  /**
   * 关闭说话人标注弹窗
   */
  closeSpeakerModal() {
    this.setData({ showSpeakerModal: false })
  },

  /**
   * 阻止事件冒泡（用于弹窗内容区域）
   */
  doNothing() {
    // 空函数，用于阻止点击事件冒泡到遮罩层
  },

  /**
   * 选择联系人标注
   */
  async selectContact(e) {
    const contactId = e.currentTarget.dataset.contactId
    const { currentSpeaker, meetingId } = this.data
    
    showLoading('标注中...')
    
    try {
      await API.mapSpeaker(meetingId, {
        speaker_id: currentSpeaker,
        contact_id: contactId
      })
      
      showToast('标注成功', 'success')
      this.closeSpeakerModal()
      this.loadSpeakerMap()
    } catch (error) {
      console.error('标注失败:', error)
      showToast('标注失败', 'error')
    } finally {
      hideLoading()
    }
  },

  /**
   * 自定义名称标注
   */
  async customNameAnnotation() {
    const { currentSpeaker, meetingId } = this.data
    
    wx.showModal({
      title: '自定义名称',
      editable: true,
      placeholderText: '请输入说话人姓名',
      success: async (res) => {
        if (res.confirm && res.content) {
          showLoading('标注中...')
          
          try {
            await API.mapSpeaker(meetingId, {
              speaker_id: currentSpeaker,
              custom_name: res.content
            })
            
            showToast('标注成功', 'success')
            this.closeSpeakerModal()
            this.loadSpeakerMap()
          } catch (error) {
            console.error('标注失败:', error)
            showToast('标注失败', 'error')
          } finally {
            hideLoading()
          }
        }
      }
    })
  },

  /**
   * 获取说话人显示名称
   */
  getSpeakerName(speakerId) {
    return this.data.speakerMap[speakerId] || speakerId
  }
})

