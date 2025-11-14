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
        // 如果是字符串，尝试判断格式
        if (typeof data === 'string') {
          // 如果以 # 开头，可能是 Markdown 格式
          if (data.trim().startsWith('#') || data.trim().startsWith('-') || data.trim().startsWith('*')) {
            console.log('[思维导图] 检测到 Markdown 格式，进行解析')
            const nodes = this.parseMarkdown(data)
            this.setData({ nodes })
            return
          }

          // 否则尝试解析为 JSON
          try {
            const mindMapData = JSON.parse(data)
            if (Array.isArray(mindMapData)) {
              const nodes = []
              mindMapData.forEach(root => {
                this.flattenNode(root, 0, nodes)
              })
              this.setData({ nodes })
              return
            }
          } catch (e) {
            console.warn('[思维导图] JSON 解析失败，尝试作为纯文本处理')
          }
        } else if (Array.isArray(data)) {
          // JSON 数组格式（通义听悟）
          const nodes = []
          data.forEach(root => {
            this.flattenNode(root, 0, nodes)
          })
          this.setData({ nodes })
          return
        }

        console.warn('思维导图数据格式不正确:', data)
        this.setData({ nodes: [] })
      } catch (error) {
        console.error('解析思维导图数据失败:', error)
        this.setData({ nodes: [] })
      }
    },

    /**
     * 解析 Markdown 格式的思维导图
     */
    parseMarkdown(markdown) {
      const lines = markdown.split('\n')
      const nodes = []
      let currentLevel = 0

      lines.forEach(line => {
        const trimmed = line.trim()
        if (!trimmed) return

        // 检测标题（# ## ###）
        const headerMatch = trimmed.match(/^(#{1,6})\s+(.+)$/)
        if (headerMatch) {
          const level = headerMatch[1].length - 1 // # = level 0, ## = level 1
          const title = headerMatch[2].trim()
          nodes.push({
            id: `h-${nodes.length}`,
            title: title,
            level: level
          })
          currentLevel = level
          return
        }

        // 检测列表项（- * 或数字）
        const listMatch = trimmed.match(/^[-*+]\s+(.+)$/) || trimmed.match(/^\d+\.\s+(.+)$/)
        if (listMatch) {
          const title = listMatch[1].trim()
          // 计算缩进层级
          const indent = line.match(/^(\s*)/)[1].length
          const level = currentLevel + 1 + Math.floor(indent / 2)

          nodes.push({
            id: `l-${nodes.length}`,
            title: title,
            level: level
          })
        }
      })

      return nodes
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

