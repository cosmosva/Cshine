/**
 * API 配置
 */

// API 基础地址
// const API_BASE_URL = 'http://172.20.10.52:8000'  // 开发环境（真机测试用）
const API_BASE_URL = 'http://localhost:8000'  // 模拟器用
// const API_BASE_URL = 'https://api.yourdomain.com'  // 生产环境

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
  
  // 文件上传
  UPLOAD_AUDIO: '/api/v1/upload/audio'
}

module.exports = {
  API_BASE_URL,
  STORAGE_KEYS,
  API_ENDPOINTS
}

