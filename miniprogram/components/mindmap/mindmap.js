/**
 * 思维导图组件
 */
Component({
  properties: {
    // 思维导图数据（JSON 字符串或对象）
    data: {
      type: String,
      value: '',
      observer: 'parseData'
    }
  },

  data: {
    nodes: [] // 扁平化的节点列表
  },

  methods: {
    /**
     * 解析思维导图数据
     */
    parseData(data) {
      if (!data) {
        this.setData({ nodes: [] })
        return
      }

      try {
        // 如果是字符串，先解析为对象
        const mindMapData = typeof data === 'string' ? JSON.parse(data) : data
        
        // 通义听悟返回的格式是数组
        if (Array.isArray(mindMapData)) {
          const nodes = []
          mindMapData.forEach(root => {
            this.flattenNode(root, 0, nodes)
          })
          this.setData({ nodes })
        } else {
          console.warn('思维导图数据格式不正确:', mindMapData)
          this.setData({ nodes: [] })
        }
      } catch (error) {
        console.error('解析思维导图数据失败:', error)
        this.setData({ nodes: [] })
      }
    },

    /**
     * 递归扁平化节点
     * @param {Object} node - 节点对象
     * @param {Number} level - 层级
     * @param {Array} result - 结果数组
     */
    flattenNode(node, level, result) {
      if (!node) return

      // 添加当前节点
      result.push({
        id: `${level}-${result.length}`,
        title: node.Title || '',
        time: this.formatTime(node.BeginTime),
        level: level
      })

      // 递归处理子节点
      if (node.Topic && Array.isArray(node.Topic)) {
        node.Topic.forEach(child => {
          this.flattenNode(child, level + 1, result)
        })
      }
    },

    /**
     * 格式化时间（毫秒 → MM:SS）
     */
    formatTime(ms) {
      if (!ms || ms === 0) return ''
      
      const seconds = Math.floor(ms / 1000)
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      
      return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`
    }
  }
})

