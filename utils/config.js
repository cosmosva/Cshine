/**
 * API 配置
 */

// 环境配置
const ENV = 'production'  // 'development' | 'production'

// API 基础地址配置
const API_CONFIG = {
  development: 'http://192.168.80.50:8000',  // 开发环境（真机测试用）
  // development: 'http://localhost:8000',     // 模拟器用
  production: 'https://cshine.xuyucloud.com'  // 生产环境
}

// 根据环境选择 API 地址
const API_BASE_URL = API_CONFIG[ENV]

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
  
  // 文件上传
  UPLOAD_AUDIO: '/api/v1/upload/audio'
}

module.exports = {
  API_BASE_URL,
  STORAGE_KEYS,
  API_ENDPOINTS
}

