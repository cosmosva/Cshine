/**
 * 会议音频上传页
 */

const API = require('../../utils/api')
const { showToast, showLoading, hideLoading } = require('../../utils/toast')

Page({
  data: {
    // 模式：upload（上传）/ view（查看进度）
    mode: 'upload',
    
    // 会议信息
    meetingId: '',
    title: '',
    participants: '',  // 逗号分隔
    meetingDate: '',
    audioPath: '',
    audioUrl: '',
    audioDuration: 0,
    
    // 处理状态
    status: 'idle',  // idle / uploading / processing / completed / failed
    progress: 0,
    errorMessage: '',
    
    // 轮询定时器
    pollingTimer: null,
    
    // 日期选择器
    maxDate: ''
  },

  onLoad(options) {
    // 设置最大日期为今天
    const today = new Date()
    this.setData({
      maxDate: this.formatDate(today)
    })
    
    // 判断模式
    if (options.meetingId) {
      // 查看模式
      this.setData({
        mode: 'view',
        meetingId: options.meetingId
      })
      this.loadMeetingStatus()
    } else if (options.fileName) {
      // 从列表页跳转过来的上传模式
      this.setData({ 
        mode: 'upload',
        audioDuration: parseInt(options.duration) || 0
      })
      
      // 从全局变量获取文件信息
      const uploadFile = getApp().globalData.uploadFile
      if (uploadFile) {
        this.setData({
          audioPath: uploadFile.path,
          title: decodeURIComponent(options.fileName),
          audioDuration: uploadFile.duration || 0
        })
        
        // 获取 folderId
        const folderId = options.folderId ? parseInt(options.folderId) : null
        this._folderId = folderId
        
        // 自动开始上传
        this.startUpload()
      }
    } else {
      // 普通上传模式
      this.setData({ mode: 'upload' })
    }
  },

  onUnload() {
    // 清除定时器
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer)
    }
  },

  /**
   * 选择音频文件
   */
  chooseAudio() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['mp3', 'm4a', 'wav', 'aac'],
      success: (res) => {
        const file = res.tempFiles[0]
        
        // 检查文件大小（最大500MB）
        if (file.size > 500 * 1024 * 1024) {
          showToast('文件大小不能超过500MB', 'error')
          return
        }
        
        this.setData({
          audioPath: file.path,
          audioDuration: 0  // 微信小程序无法直接获取音频时长
        })
        
        showToast('文件选择成功', 'success')
      },
      fail: (err) => {
        console.error('选择文件失败:', err)
        showToast('选择文件失败', 'error')
      }
    })
  },

  /**
   * 输入标题
   */
  onTitleInput(e) {
    this.setData({ title: e.detail.value })
  },

  /**
   * 输入参会人
   */
  onParticipantsInput(e) {
    this.setData({ participants: e.detail.value })
  },

  /**
   * 选择日期
   */
  onDateChange(e) {
    this.setData({ meetingDate: e.detail.value })
  },

  /**
   * 提交上传
   */
  async submitUpload() {
    // 验证
    if (!this.data.title) {
      showToast('请输入会议主题', 'error')
      return
    }
    
    if (!this.data.audioPath) {
      showToast('请选择音频文件', 'error')
      return
    }
    
    await this.startUpload()
  },

  /**
   * 开始上传流程
   */
  async startUpload() {
    this.setData({ status: 'uploading', progress: 10 })
    
    try {
      // 1. 上传音频文件到 OSS (带进度)
      console.log('开始上传音频文件:', this.data.audioPath)
      const uploadData = await this.uploadAudioWithProgress(this.data.audioPath)
      console.log('上传响应（已解包）:', uploadData)
      
      if (!uploadData || !uploadData.file_url) {
        throw new Error('文件上传失败，未返回文件URL')
      }
      
      this.setData({ 
        audioUrl: uploadData.file_url,
        audioDuration: uploadData.duration || this.data.audioDuration,
        progress: 30
      })
      
      console.log('音频上传成功，URL:', uploadData.file_url)
      
      // 2. 创建会议纪要
      const participants = this.data.participants
        ? this.data.participants.split(/[，,]/).map(p => p.trim()).filter(p => p)
        : []
      
      const meetingData = {
        title: this.data.title,
        participants: participants,
        meeting_date: this.data.meetingDate || null,
        audio_url: this.data.audioUrl,
        audio_duration: this.data.audioDuration
      }
      
      // 如果有 folderId，添加到数据中
      if (this._folderId) {
        meetingData.folder_id = this._folderId
      }
      
      console.log('创建会议纪要，数据:', meetingData)
      const meetingResult = await API.createMeeting(meetingData)
      console.log('创建会议响应（已解包）:', meetingResult)
      
      if (!meetingResult || !meetingResult.id) {
        throw new Error('创建会议失败，未返回会议ID')
      }
      
      this.setData({
        meetingId: meetingResult.id,
        status: 'processing',
        progress: 50,
        mode: 'view'
      })
      
      showToast('上传成功，开始处理...', 'success')
      
      // 3. 开始轮询状态
      this.startPolling()
      
    } catch (error) {
      console.error('上传失败:', error)
      this.setData({
        status: 'failed',
        errorMessage: error.message || '上传失败，请重试'
      })
      showToast(this.data.errorMessage, 'error')
    }
  },

  /**
   * 上传音频文件到 OSS（带进度监听）
   */
  uploadAudioWithProgress(filePath) {
    return new Promise((resolve, reject) => {
      // 先获取 OSS 签名
      API.getOssSignature()
        .then(ossData => {
          console.log('OSS 签名数据:', ossData)
          
          // 构建 OSS 上传参数
          const uploadTask = wx.uploadFile({
            url: ossData.host,
            filePath: filePath,
            name: 'file',
            formData: {
              key: ossData.key,
              policy: ossData.policy,
              OSSAccessKeyId: ossData.accessid,
              signature: ossData.signature,
              success_action_status: '200'
            },
            success: (res) => {
              if (res.statusCode === 200) {
                const fileUrl = `${ossData.host}/${ossData.key}`
                resolve({
                  file_url: fileUrl,
                  duration: this.data.audioDuration
                })
              } else {
                reject(new Error(`上传失败: ${res.statusCode}`))
              }
            },
            fail: (err) => {
              console.error('OSS 上传失败:', err)
              reject(new Error('上传失败，请重试'))
            }
          })

          // 监听上传进度
          uploadTask.onProgressUpdate((res) => {
            const progress = Math.min(res.progress, 30) // 上传进度占 0-30%
            this.setData({ progress })
          })
        })
        .catch(err => {
          console.error('获取 OSS 签名失败:', err)
          reject(new Error('获取上传凭证失败'))
        })
    })
  },

  /**
   * 开始轮询会议处理状态
   */
  startPolling() {
    // 清除之前的定时器
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer)
    }
    
    // 立即查询一次
    this.checkMeetingStatus()
    
    // 每5秒查询一次
    const timer = setInterval(() => {
      this.checkMeetingStatus()
    }, 5000)
    
    this.setData({ pollingTimer: timer })
  },

  /**
   * 检查会议处理状态
   */
  async checkMeetingStatus() {
    try {
      const statusData = await API.getMeetingStatus(this.data.meetingId)
      console.log('状态查询响应（已解包）:', statusData)
      
      if (statusData) {
        const { status, progress, message, error } = statusData
        
        this.setData({
          status: status,
          progress: progress || this.data.progress,
          errorMessage: error || ''
        })
        
        // 如果已完成或失败，停止轮询
        if (status === 'completed') {
          this.stopPolling()
          showToast('处理完成！', 'success')
          
          // 2秒后跳转到详情页
          setTimeout(() => {
            wx.redirectTo({
              url: `/pages/meeting/detail?id=${this.data.meetingId}`
            })
          }, 2000)
        } else if (status === 'failed') {
          this.stopPolling()
          showToast('处理失败', 'error')
        }
      }
    } catch (error) {
      console.error('查询状态失败:', error)
    }
  },

  /**
   * 加载会议状态（查看模式）
   */
  async loadMeetingStatus() {
    try {
      const meeting = await API.getMeetingDetail(this.data.meetingId)
      console.log('会议详情响应（已解包）:', meeting)
      
      if (meeting) {
        this.setData({
          title: meeting.title,
          status: meeting.status,
          progress: meeting.status === 'completed' ? 100 : 
                   meeting.status === 'processing' ? 50 : 0
        })
        
        // 如果还在处理中，开始轮询
        if (meeting.status === 'processing' || meeting.status === 'pending') {
          this.startPolling()
        }
      }
    } catch (error) {
      console.error('加载会议状态失败:', error)
      showToast('加载失败', 'error')
    }
  },

  /**
   * 停止轮询
   */
  stopPolling() {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer)
      this.setData({ pollingTimer: null })
    }
  },

  /**
   * 格式化日期
   */
  formatDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  /**
   * 返回列表
   */
  backToList() {
    wx.navigateBack()
  }
})

