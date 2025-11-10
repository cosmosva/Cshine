/**
 * API 配置
 */

// API 基础地址配置
const API_CONFIG = {
  development: 'http://localhost:8000',           // 开发环境（模拟器）
  // development: 'http://192.168.3.206:8000',   // 真机测试时取消注释并填写电脑 IP
  production: 'https://cshine.xuyucloud.com'      // 生产环境
}

/**
 * 自动检测运行环境
 * - 开发工具、开发版 → development
 * - 体验版、正式版 → production
 */
function getEnvironment() {
  const accountInfo = wx.getAccountInfoSync()
  const envVersion = accountInfo.miniProgram.envVersion
  
  // envVersion 可能的值：
  // 'develop'  - 开发版
  // 'trial'    - 体验版
  // 'release'  - 正式版
  // undefined  - 开发工具
  
  // 体验版和正式版都使用生产环境
  if (envVersion === 'release' || envVersion === 'trial') {
    return 'production'
  } else {
    return 'development'  // 开发工具和开发版用开发环境
  }
}

// 根据环境选择 API 地址
const ENV = getEnvironment()
const API_BASE_URL = API_CONFIG[ENV]

console.log('🌍 当前运行环境:', ENV)
console.log('🔗 API 地址:', API_BASE_URL)

// 存储键名
const STORAGE_KEYS = {
  TOKEN: 'cshine_token',
  USER_INFO: 'cshine_user_info',
  USER_ID: 'cshine_user_id'
}

// API 端点
const API_ENDPOINTS = {
  // 认证相关
  AUTH_LOGIN: '/api/v1/auth/login',
  AUTH_ME: '/api/v1/auth/me',
  
  // 闪记相关
  FLASH_CREATE: '/api/v1/flash/create',
  FLASH_LIST: '/api/v1/flash/list',
  FLASH_DETAIL: '/api/v1/flash/',  // 需要拼接 ID
  FLASH_UPDATE: '/api/v1/flash/',  // 需要拼接 ID
  FLASH_DELETE: '/api/v1/flash/',  // 需要拼接 ID
  FLASH_FAVORITE: '/api/v1/flash/',  // 需要拼接 ID/favorite
  FLASH_AI_STATUS: '/api/v1/flash/',  // 需要拼接 ID/ai-status
  
  // 会议纪要相关
  MEETING_CREATE: '/api/v1/meeting/create',
  MEETING_LIST: '/api/v1/meeting/list',
  MEETING_DETAIL: '/api/v1/meeting/',  // 需要拼接 ID
  MEETING_UPDATE: '/api/v1/meeting/',  // 需要拼接 ID
  MEETING_DELETE: '/api/v1/meeting/',  // 需要拼接 ID
  MEETING_STATUS: '/api/v1/meeting/',  // 需要拼接 ID/status

  // 知识库相关
  FOLDER_CREATE: '/api/v1/folders',
  FOLDER_LIST: '/api/v1/folders',
  FOLDER_UPDATE: '/api/v1/folders/',  // 需要拼接 ID
  FOLDER_DELETE: '/api/v1/folders/',  // 需要拼接 ID

  // 文件上传
  UPLOAD_AUDIO: '/api/v1/upload/audio'
}

module.exports = {
  API_BASE_URL,
  STORAGE_KEYS,
  API_ENDPOINTS
}

