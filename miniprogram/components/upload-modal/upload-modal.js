Component({
  properties: {
    show: {
      type: Boolean,
      value: false
    }
  },

  data: {
    title: '上传音频',
    status: 'uploading', // uploading, success, error
    statusText: '正在上传...',
    progress: 0
  },

  methods: {
    // 开始上传
    startUpload(options = {}) {
      const { title = '上传音频' } = options
      
      this.setData({
        title,
        status: 'uploading',
        statusText: '正在上传音频...',
        progress: 10
      })
    },

    // 更新进度
    updateProgress(progress, statusText) {
      this.setData({
        progress: Math.min(progress, 99),
        statusText: statusText || this.data.statusText
      })
    },

    // 上传成功
    showSuccess(message = '上传成功') {
      this.setData({
        status: 'success',
        statusText: message,
        progress: 100
      })

      // 2秒后自动关闭
      setTimeout(() => {
        this.onClose()
      }, 2000)
    },

    // 上传失败
    showError(message = '上传失败') {
      this.setData({
        status: 'error',
        statusText: message,
        progress: 0
      })
    },

    // 关闭模态框
    onClose() {
      this.triggerEvent('close', {
        status: this.data.status
      })
    },

    // 点击遮罩（上传中不允许关闭）
    onMaskTap() {
      if (this.data.status !== 'uploading') {
        this.onClose()
      }
    }
  }
})

