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

