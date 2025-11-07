// 编辑闪记页面
const api = require('../../utils/api')
const { showSuccess, showError, showLoading, hideLoading } = require('../../utils/toast')

Page({
  data: {
    flashId: '',
    title: '',
    content: '',
    category: '工作',
    summary: '',
    keywords: [],
    categories: ['工作', '生活', '学习', '灵感', '其他'],
    isLoading: true,
    hasChanged: false  // 标记是否有修改
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
  },

  /**
   * 加载闪记详情
   */
  async loadFlashDetail() {
    try {
      this.setData({ isLoading: true })
      
      const flash = await api.getFlashDetail(this.data.flashId)
      console.log('加载闪记数据:', flash)
      
      this.setData({
        title: flash.title || '',
        content: flash.content || '',
        category: flash.category || '工作',
        summary: flash.summary || '',
        keywords: flash.keywords || [],
        isLoading: false
      })
    } catch (error) {
      console.error('加载失败:', error)
      showError('加载失败')
      this.setData({ isLoading: false })
      
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  /**
   * 标题输入
   */
  onTitleInput(e) {
    this.setData({
      title: e.detail.value,
      hasChanged: true
    })
  },

  /**
   * 内容输入
   */
  onContentInput(e) {
    this.setData({
      content: e.detail.value,
      hasChanged: true
    })
  },

  /**
   * 选择分类
   */
  onCategorySelect(e) {
    const category = e.currentTarget.dataset.category
    this.setData({
      category,
      hasChanged: true
    })
  },

  /**
   * 取消编辑
   */
  onCancel() {
    if (this.data.hasChanged) {
      wx.showModal({
        title: '提示',
        content: '修改尚未保存，确定要放弃吗？',
        confirmText: '放弃',
        confirmColor: '#FF4D4F',
        success: (res) => {
          if (res.confirm) {
            wx.navigateBack()
          }
        }
      })
    } else {
      wx.navigateBack()
    }
  },

  /**
   * 保存修改
   */
  async onSave() {
    // 验证必填字段
    if (!this.data.content.trim()) {
      showError('内容不能为空')
      return
    }

    try {
      showLoading('保存中...')

      const updateData = {
        title: this.data.title.trim() || undefined,
        content: this.data.content.trim(),
        category: this.data.category
      }

      await api.updateFlash(this.data.flashId, updateData)

      hideLoading()
      showSuccess('保存成功')

      // 标记为已保存
      this.setData({ hasChanged: false })

      // 返回上一页
      setTimeout(() => {
        wx.navigateBack()
      }, 1000)
    } catch (error) {
      console.error('保存失败:', error)
      hideLoading()
      showError('保存失败')
    }
  }
})

