/**
 * AI 模型选择器组件
 */

const api = require('../../utils/api')

Component({
  /**
   * 组件的属性列表
   */
  properties: {
    // 是否显示
    show: {
      type: Boolean,
      value: false
    },
    // 当前选中的模型ID
    value: {
      type: String,
      value: ''
    }
  },

  /**
   * 组件的初始数据
   */
  data: {
    models: [],        // 可用模型列表
    selectedId: '',    // 选中的模型ID
    selectedName: '',  // 选中的模型名称
    loading: false,    // 加载状态
    providerNames: {   // 提供商名称映射
      'openai': 'OpenAI',
      'anthropic': 'Anthropic',
      'doubao': '字节豆包',
      'qwen': '阿里通义'
    }
  },

  /**
   * 组件的方法列表
   */
  methods: {
    /**
     * 打开选择器时加载模型列表
     */
    onShow() {
      if (this.data.show && this.data.models.length === 0) {
        this.loadModels()
      }
    },

    /**
     * 加载可用模型列表
     */
    async loadModels() {
      this.setData({ loading: true })
      
      try {
        const res = await api.getAvailableModels()
        console.log('📡 AI 模型列表 API 响应:', res)
        
        if (res.code === 200) {
          const items = res.data?.items || []
          console.log('✅ 加载到的模型列表:', items)
          
          this.setData({
            models: items,
            loading: false
          })
          
          // 如果有默认模型且当前未选择，自动选择默认模型
          const defaultModel = items.find(m => m.is_default)
          if (!this.data.value && defaultModel) {
            console.log('🎯 自动选择默认模型:', defaultModel.name)
            this.setData({
              selectedId: defaultModel.id,
              selectedName: defaultModel.name
            })
          }
        } else {
          console.error('❌ 加载模型列表失败:', {
            code: res.code,
            message: res.message,
            data: res.data
          })
          this.setData({ loading: false })
        }
      } catch (error) {
        console.error('❌ 加载模型列表异常:', error)
        this.setData({ loading: false })
      }
    },

    /**
     * 选择模型
     */
    onSelectModel(e) {
      const { id, name } = e.currentTarget.dataset
      this.setData({
        selectedId: id,
        selectedName: name
      })
    },

    /**
     * 确认选择
     */
    onConfirm() {
      this.triggerEvent('confirm', {
        id: this.data.selectedId,
        name: this.data.selectedName
      })
      this.onClose()
    },

    /**
     * 关闭选择器
     */
    onClose() {
      this.triggerEvent('close')
    }
  },

  /**
   * 生命周期函数
   */
  lifetimes: {
    attached() {
      // 组件附加时，设置初始选中值
      this.setData({
        selectedId: this.data.value || ''
      })
    }
  },

  /**
   * 监听属性变化
   */
  observers: {
    'show': function(show) {
      if (show) {
        this.onShow()
      }
    },
    'value': function(value) {
      this.setData({
        selectedId: value || ''
      })
    }
  }
})

