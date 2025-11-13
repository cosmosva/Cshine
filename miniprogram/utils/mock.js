/**
 * Mock 数据生成器
 * 用于前端开发时模拟后端数据
 */

const { formatRelativeTime } = require('./format')

/**
 * 生成随机 UUID
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

/**
 * 生成随机日期
 * @param {number} daysAgo - 多少天前
 */
function generateDate(daysAgo = 0) {
  const date = new Date()
  date.setDate(date.getDate() - daysAgo)
  date.setHours(Math.floor(Math.random() * 24))
  date.setMinutes(Math.floor(Math.random() * 60))
  return date.toISOString()
}

/**
 * Mock 闪记数据
 */
const mockFlashCategories = ['工作', '生活', '学习', '创意', '健康']
const mockFlashTitles = [
  '产品创意：AI语音记录工具',
  '读书笔记：认知觉醒',
  '每周目标：完成PRD文档',
  '灵感闪现：短视频内容策划',
  '学习计划：前端框架深入',
  '健康提醒：坚持每天运动',
  '项目复盘：上周工作总结',
  '用户反馈：功能优化建议',
  '技术方案：数据库设计思路',
  '会议要点：产品评审会议'
]

const mockFlashContents = [
  '今天突然想到一个产品创意，可以做一个AI驱动的语音记录工具，帮助用户随时捕捉灵感。结合大模型自动生成摘要，面向知识工作者这个群体。核心功能包括快速录音、智能转写、AI摘要生成等。',
  '读完《认知觉醒》这本书，最大的收获是理解了元认知的重要性。我们要学会跳出思维定式，用第三视角观察自己的思考过程。书中提到的专注力训练方法很实用，准备尝试番茄工作法。',
  '本周的主要目标是完成产品需求文档的撰写。需要包含用户分析、功能设计、技术架构等模块。预计工作量3-5天，deadline是周五下班前。加油！',
  '刷短视频的时候突然想到，可以做一个系列内容，主题是「3分钟了解AI工具」。每期介绍一个实用的AI产品，包括ChatGPT、Midjourney、Notion AI等。目标受益人群是对AI感兴趣但不知从何入手的普通用户。',
  '最近在学习React和Vue的底层原理，发现虚拟DOM的diff算法非常巧妙。准备写一篇技术博客，深入解析这部分内容。同时也要动手实现一个简易版本，加深理解。',
  '新年健康计划：每天至少运动30分钟，可以是跑步、游泳或者健身房训练。目标是3个月瘦10斤，同时改善睡眠质量。已经购买了运动装备，明天开始执行！',
  '上周工作复盘：完成了两个新功能的开发，修复了5个bug。遇到的主要问题是性能优化，通过代码重构和缓存策略得到解决。下周重点是做好单元测试覆盖。',
  '收到用户反馈说搜索功能不够智能，希望支持模糊匹配和语义搜索。这个建议很有价值，可以加入V2.0的规划中。技术上需要引入向量数据库和Embedding技术。',
  '数据库设计方案：用户表、闪记表、会议表、标签表、关联表。需要考虑数据量增长后的分库分表策略。音频文件单独存储在OSS，数据库只保存URL引用。',
  '产品评审会议纪要：确定了MVP功能范围，包括闪记和会议纪要两大核心功能。技术栈选型为微信小程序+FastAPI+PostgreSQL。项目预计开发周期12周，分3个阶段进行。'
]

const mockKeywords = [
  ['产品', 'AI', '创意', '工具'],
  ['读书', '认知', '学习', '成长'],
  ['计划', '目标', 'PRD', '文档'],
  ['短视频', '内容', 'AI工具', '创作'],
  ['前端', 'React', 'Vue', '技术'],
  ['健康', '运动', '习惯', '目标'],
  ['工作', '复盘', '总结', '优化'],
  ['反馈', '搜索', '功能', '优化'],
  ['数据库', '设计', '架构', '方案'],
  ['会议', '评审', '功能', '开发']
]

/**
 * 生成单条闪记数据
 * @param {number} index - 索引
 * @param {number} daysAgo - 多少天前
 */
function generateFlashItem(index = 0, daysAgo = 0) {
  const idx = index % mockFlashTitles.length
  return {
    id: generateUUID(),
    title: mockFlashTitles[idx],
    content: mockFlashContents[idx],
    summary: mockFlashTitles[idx], // 简化处理，直接用标题作为摘要
    keywords: mockKeywords[idx],
    category: mockFlashCategories[Math.floor(Math.random() * mockFlashCategories.length)],
    audio_url: 'https://example.com/audio/' + generateUUID() + '.mp3',
    audio_duration: Math.floor(Math.random() * 180) + 20, // 20-200秒
    is_favorite: Math.random() > 0.8, // 20%概率收藏
    created_at: generateDate(daysAgo),
    updated_at: generateDate(daysAgo)
  }
}

/**
 * 生成闪记列表
 * @param {number} count - 数量
 */
function generateFlashList(count = 10) {
  const list = []
  for (let i = 0; i < count; i++) {
    list.push(generateFlashItem(i, Math.floor(i / 2))) // 每两条相差一天
  }
  return list
}

/**
 * 生成用户信息
 */
function generateUserInfo() {
  return {
    id: generateUUID(),
    nickname: 'Cshine用户',
    avatar: 'https://thirdwx.qlogo.cn/mmopen/vi_32/placeholder/132',
    total_flashes: Math.floor(Math.random() * 100) + 50,
    total_meetings: Math.floor(Math.random() * 20) + 5,
    total_duration: Math.floor(Math.random() * 3600) + 600, // 总时长（秒）
    created_at: generateDate(30),
    subscription_tier: 'free'
  }
}

/**
 * 生成统计数据
 */
function generateStats() {
  return {
    today: {
      flashes: Math.floor(Math.random() * 10),
      duration: Math.floor(Math.random() * 600)
    },
    week: {
      flashes: Math.floor(Math.random() * 50),
      duration: Math.floor(Math.random() * 3600)
    },
    month: {
      flashes: Math.floor(Math.random() * 200),
      duration: Math.floor(Math.random() * 10800)
    },
    category_distribution: mockFlashCategories.map(cat => ({
      category: cat,
      count: Math.floor(Math.random() * 30) + 5
    }))
  }
}

/**
 * 模拟 API 请求延迟
 * @param {number} delay - 延迟时间（毫秒）
 */
function mockDelay(delay = 500) {
  return new Promise(resolve => setTimeout(resolve, delay))
}

/**
 * 模拟 API 响应
 * @param {any} data - 返回数据
 * @param {number} delay - 延迟时间
 */
async function mockApiResponse(data, delay = 500) {
  await mockDelay(delay)
  return {
    code: 200,
    message: 'success',
    data
  }
}

module.exports = {
  generateUUID,
  generateDate,
  generateFlashItem,
  generateFlashList,
  generateUserInfo,
  generateStats,
  mockDelay,
  mockApiResponse
}

