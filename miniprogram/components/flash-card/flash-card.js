// 闪记卡片组件
const { formatRelativeTime, formatDuration } = require('../../utils/format')
const { vibrateShort } = require('../../utils/toast')

Component({
  properties: {
    // 闪记数据
    item: {
      type: Object,
      value: {},
      observer: 'onItemChange'
    }
  },

  data: {
    displayTime: '',           // 显示的时间文本
    formattedDuration: '',     // 格式化的音频时长
    categoryIcon: ''           // 分类图标
  },

  lifetimes: {
    attached() {
      this.updateDisplayData()
    }
  },

  methods: {
    /**
     * 数据变化时更新显示
     */
    onItemChange() {
      this.updateDisplayData()
    },

    /**
     * 更新显示数据
     */
    updateDisplayData() {
      const item = this.data.item
      if (!item) return

      // 格式化时间
      const displayTime = item.created_at 
        ? formatRelativeTime(item.created_at) 
        : ''

      // 格式化音频时长
      const formattedDuration = item.audio_duration 
        ? formatDuration(item.audio_duration) 
        : ''

      // 分类图标
      const categoryIcons = {
        '工作': '💼',
        '生活': '🏠',
        '学习': '📚',
        '创意': '💡',
        '健康': '❤️'
      }
      const categoryIcon = categoryIcons[item.category] || '📝'

      this.setData({
        displayTime,
        formattedDuration,
        categoryIcon
      })
    },

    /**
     * 点击卡片
     */
    onCardTap() {
      vibrateShort('light')
      this.triggerEvent('cardtap', { item: this.data.item })
    },

    /**
     * 点击收藏
     */
    onFavorite(e) {
      // catchtap 已经阻止冒泡，无需手动调用 stopPropagation
      vibrateShort('light')
      
      const item = this.data.item
      const newFavoriteStatus = !item.is_favorite
      
      // 触发事件通知父组件（实际项目中应该调用API）
      this.setData({
        'item.is_favorite': newFavoriteStatus
      })
      
      // 触发收藏事件
      this.triggerEvent('favorite', {
        id: item.id,
        is_favorite: newFavoriteStatus
      })
    }
  }
})

