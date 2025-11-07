// index.js
const api = require('../../utils/api')
const { showSuccess, showError, showLoading, hideLoading, showToast } = require('../../utils/toast')

const app = getApp()

Page({
  data: {
    // 筛选选项 - 使用统一的分类
    filterOptions: ['最近记录', '工作', '生活', '学习', '灵感', '其他'],
    activeFilter: '最近记录',
    
    // 闪记列表
    flashList: [],
    isLoading: true,
    isRefreshing: false,
    
    // 统计
    todayCount: 0,
    
    // 分页
    currentPage: 1,
    hasMore: true
  },

  /**
   * 页面加载
   */
  async onLoad() {
    console.log('首页加载')
    
    // 确保已登录
    const isLoggedIn = await app.ensureLogin()
    if (!isLoggedIn) {
      showError('登录失败，请重试')
      return
    }
    
    // 加载数据
    this.loadFlashList()
  },

  /**
   * 页面显示
   */
  onShow() {
    console.log('首页显示')
    
    // 页面显示时刷新列表（获取最新数据）
    if (this.data.flashList.length > 0) {
      this.loadFlashList(true)
    }
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    console.log('下拉刷新')
    this.loadFlashList(true).finally(() => {
      wx.stopPullDownRefresh()
    })
  },

  /**
   * 加载闪记列表（真实 API）
   * @param {boolean} silent 是否静默加载（不显示 loading）
   */
  async loadFlashList(silent = false) {
    if (!silent) {
      this.setData({ isLoading: true })
    }
    
    try {
      // 构建查询参数
      const params = {
        page: this.data.currentPage,
        page_size: 20
      }
      
      // 分类筛选
      const activeFilter = this.data.activeFilter
      if (activeFilter && activeFilter !== '最近记录') {
        params.category = activeFilter
      }
      
      // 调用 API
      const result = await api.getFlashList(params)
      
      console.log('闪记列表加载成功:', result)
      
      // 计算今天的记录数量
      const today = new Date().toDateString()
      const todayCount = result.items.filter(item => {
        const itemDate = new Date(item.created_at).toDateString()
        return itemDate === today
      }).length
      
      this.setData({
        flashList: result.items,
        todayCount: todayCount,
        hasMore: result.total > (result.page * result.page_size),
        isLoading: false
      })
      
      console.log(`加载完成，共 ${result.total} 条，当前 ${result.items.length} 条`)
    } catch (error) {
      console.error('加载失败:', error)
      this.setData({ isLoading: false })
      
      // 静默加载失败不提示
      if (!silent) {
        showError('加载失败，请重试')
      }
    }
  },

  /**
   * 下拉刷新
   */
  async onRefresh() {
    console.log('下拉刷新')
    this.setData({ isRefreshing: true })
    
    await this.loadFlashList()
    
    // 延迟关闭刷新状态
    setTimeout(() => {
      this.setData({ isRefreshing: false })
      showSuccess('刷新成功')
    }, 500)
  },

  /**
   * 筛选切换
   */
  onFilterChange(e) {
    const filter = e.currentTarget.dataset.filter
    console.log('切换筛选:', filter)
    
    this.setData({ 
      activeFilter: filter,
      currentPage: 1  // 重置页码
    })
    
    // 重新加载数据
    this.loadFlashList()
  },

  /**
   * 点击帮助按钮
   */
  onShowHelp() {
    wx.showModal({
      title: '使用帮助',
      content: '长按录音按钮开始记录，松开自动保存。上滑可以取消录音。\n\nCshine 会自动将语音转为文字，并生成智能摘要。',
      confirmText: '知道了',
      showCancel: false
    })
  },

  /**
   * 开始录音
   */
  onRecordStart() {
    console.log('开始录音')
  },

  /**
   * 录音结束
   */
  async onRecordEnd(e) {
    console.log('录音结束:', e.detail)
    const { tempFilePath, duration, fileSize } = e.detail
    
    try {
      // 1. 显示加载提示
      showLoading('上传中...')
      
      // 2. 上传音频文件
      const uploadResult = await api.uploadAudio(tempFilePath)
      console.log('音频上传成功:', uploadResult)
      
      // 3. 创建闪记记录
      hideLoading()
      showLoading('AI 正在处理...')
      
      // TODO: 这里应该等待后端 ASR 转写完成
      // 目前先创建一个临时记录
      const flashData = {
        content: '语音转写中...',  // TODO: 等待 ASR 结果
        audio_url: uploadResult.file_url,
        audio_duration: duration,
        category: '工作'
      }
      
      const createResult = await api.createFlash(flashData)
      console.log('闪记创建成功:', createResult)
      
      hideLoading()
      showSuccess('录音保存成功')
      
      // 4. 刷新列表（显示新创建的记录）
      this.loadFlashList(true)
      
      // TODO: 实际项目中可以跳转到详情页
      // wx.navigateTo({
      //   url: `/pages/detail/detail?id=${createResult.id}`
      // })
      
      // 5. 如果有音频，使用全局轮询 AI 处理状态（不会被页面刷新打断）
      console.log('🚀 准备启动全局 AI 轮询，flash_id:', createResult.id)
      if (uploadResult.file_url) {
        const app = getApp()
        app.startAIPolling(
          createResult.id,
          (result) => {
            // AI 处理完成的回调
            console.log('🎉 AI 处理完成回调:', result)
            // 刷新列表以显示最新结果
            this.loadFlashList(true)
          },
          (error) => {
            // 错误回调
            console.error('❌ AI 处理失败回调:', error)
          }
        )
      }
    } catch (error) {
      console.error('录音处理失败:', error)
      hideLoading()
      showError('保存失败，请重试')
    }
  },

  /**
   * 取消录音
   */
  onRecordCancel() {
    console.log('取消录音')
    showToast('已取消录音')
  },

  /**
   * 录音错误
   */
  onRecordError(e) {
    console.error('录音错误:', e.detail)
    const errorMsg = e.detail.error.message || '录音失败'
    showError(errorMsg)
  },

  /**
   * 轮询 AI 处理状态
   * @param {string} flashId 闪记ID
   */
  async pollAIStatus(flashId) {
    console.log('[轮询] 💫💫💫 启动 AI 状态轮询，flash_id:', flashId)
    const MAX_ATTEMPTS = 90  // 最多轮询 90 次（3 分钟）
    const POLL_INTERVAL = 2000  // 每 2 秒轮询一次（更快）
    let attempts = 0

    const poll = async () => {
      try {
        attempts++
        console.log(`[轮询 ${attempts}/${MAX_ATTEMPTS}] 🔍 查询 flash_id=${flashId}`)
        
        const result = await api.getAIStatus(flashId)
        console.log(`[轮询 ${attempts}] 📦 API 返回:`, JSON.stringify(result))
        
        const { status, content, summary, keywords, category } = result

        console.log(`[轮询 ${attempts}] 📊 AI 状态: ${status}, content: ${content ? content.substring(0, 30) + '...' : 'null'}`)

        if (status === 'completed') {
          // AI 处理完成，更新本地闪记数据
          console.log(`[轮询 ${attempts}] ✅ AI 处理完成！准备更新界面`)
          console.log(`[轮询 ${attempts}] 转写内容:`, content)
          console.log(`[轮询 ${attempts}] 分类:`, category)
          
          // 暂时不更新界面，只打印日志
          // const flashList = this.data.flashList.map(flash => {
          //   if (flash.id === flashId) {
          //     return {
          //       ...flash,
          //       content: content || flash.content,
          //       summary: summary || flash.summary,
          //       keywords: keywords || flash.keywords,
          //       category: category || flash.category
          //     }
          //   }
          //   return flash
          // })

          // this.setData({ flashList })
          showToast('AI 分析完成！')
          console.log('[轮询] ✅✅✅ 完成，停止轮询')
          return // 停止轮询
        } else if (status === 'failed') {
          // AI 处理失败
          console.error(`[轮询 ${attempts}] ❌ AI 处理失败:`, result.error)
          showError('AI 处理失败')
          return // 停止轮询
        } else if (status === 'processing' || status === 'pending') {
          // 继续轮询
          console.log(`[轮询 ${attempts}] ⏳ 状态: ${status}，继续等待...`)
          if (attempts < MAX_ATTEMPTS) {
            setTimeout(poll, POLL_INTERVAL)
          } else {
            console.warn('AI 处理超时')
            showToast('AI 处理超时，请稍后查看')
          }
        } else {
          console.warn(`[轮询 ${attempts}] ⚠️ 未知状态: ${status}`)
          // 未知状态也继续轮询
          if (attempts < MAX_ATTEMPTS) {
            setTimeout(poll, POLL_INTERVAL)
          }
        }
      } catch (error) {
        console.error(`[轮询 ${attempts}] ❌❌❌ 轮询出错:`)
        console.error(`[轮询 ${attempts}] 错误类型:`, error.constructor.name)
        console.error(`[轮询 ${attempts}] 错误消息:`, error.message)
        console.error(`[轮询 ${attempts}] 错误对象:`, error)
        
        // 出错时暂停轮询，便于查看错误
        console.error(`[轮询 ${attempts}] ⏸️ 轮询已暂停，请查看错误信息`)
        showError(`轮询出错: ${error.message || '未知错误'}`)
        
        // 不再继续轮询，避免刷屏
        // if (attempts < MAX_ATTEMPTS) {
        //   setTimeout(poll, POLL_INTERVAL)
        // }
      }
    }

    // 立即开始第一次轮询（不等待）
    console.log('[轮询] ⏰ 立即开始第一次轮询...')
    setTimeout(poll, 500)  // 只等待 0.5 秒
  },

  /**
   * 点击卡片
   */
  onCardTap(e) {
    const item = e.detail.item
    console.log('点击卡片:', item.id)
    
    // 跳转到详情页
    wx.navigateTo({
      url: `/pages/detail/detail?id=${item.id}`
    })
  },

  /**
   * 点击收藏
   */
  async onFavorite(e) {
    const { id, is_favorite } = e.detail
    console.log('切换收藏:', id, is_favorite)
    
    try {
      // 调用 API 更新收藏状态
      await api.toggleFavorite(id)
      showSuccess(is_favorite ? '已收藏' : '已取消收藏')
      
      // 可选：刷新列表
      // this.loadFlashList(true)
    } catch (error) {
      console.error('收藏操作失败:', error)
      // 恢复原状态
      const flashList = this.data.flashList.map(item => {
        if (item.id === id) {
          return { ...item, is_favorite: !is_favorite }
        }
        return item
      })
      this.setData({ flashList })
    }
  },

  /**
   * 分享
   */
  onShareAppMessage() {
    return {
      title: 'Cshine - 让你的灵感发光 ✨',
      path: '/pages/index/index',
      imageUrl: '' // TODO: 添加分享图片
    }
  }
})
