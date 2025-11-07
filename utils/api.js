/**
 * API 接口统一管理
 * 所有 API 调用都通过这个模块
 */

const { get, post, put, del, upload } = require('./request')
const { API_ENDPOINTS } = require('./config')

/**
 * ==================== 认证相关 ====================
 */

/**
 * 微信登录
 * @param {string} code 微信登录凭证
 * @param {object} userInfo 用户信息
 */
function login(code, userInfo = {}) {
  return post(API_ENDPOINTS.AUTH_LOGIN, {
    code,
    nickname: userInfo.nickname,
    avatar: userInfo.avatar
  }, { needAuth: false })
}

/**
 * 获取当前用户信息
 */
function getUserInfo() {
  return get(API_ENDPOINTS.AUTH_ME)
}

/**
 * ==================== 闪记相关 ====================
 */

/**
 * 创建闪记
 * @param {object} data 闪记数据
 */
function createFlash(data) {
  return post(API_ENDPOINTS.FLASH_CREATE, data, { showLoad: true })
}

/**
 * 获取闪记列表
 * @param {object} params 查询参数
 */
function getFlashList(params = {}) {
  const defaultParams = {
    page: 1,
    page_size: 20
  }
  return get(API_ENDPOINTS.FLASH_LIST, { ...defaultParams, ...params })
}

/**
 * 获取闪记详情
 * @param {string} flashId 闪记ID
 */
function getFlashDetail(flashId) {
  return get(API_ENDPOINTS.FLASH_DETAIL + flashId)
}

/**
 * 更新闪记
 * @param {string} flashId 闪记ID
 * @param {object} data 更新的数据
 */
function updateFlash(flashId, data) {
  return put(API_ENDPOINTS.FLASH_UPDATE + flashId, data)
}

/**
 * 删除闪记
 * @param {string} flashId 闪记ID
 */
function deleteFlash(flashId) {
  return del(API_ENDPOINTS.FLASH_DELETE + flashId)
}

/**
 * 切换收藏状态
 * @param {string} flashId 闪记ID
 */
function toggleFavorite(flashId) {
  return put(API_ENDPOINTS.FLASH_FAVORITE + flashId + '/favorite')
}

/**
 * 查询 AI 处理状态
 * @param {string} flashId 闪记ID
 */
function getAIStatus(flashId) {
  return get(API_ENDPOINTS.FLASH_AI_STATUS + flashId + '/ai-status')
}

/**
 * ==================== 文件上传 ====================
 */

/**
 * 上传音频文件
 * @param {string} filePath 文件路径
 */
function uploadAudio(filePath) {
  return upload(API_ENDPOINTS.UPLOAD_AUDIO, filePath, {}, { showLoad: true })
}

/**
 * ==================== 导出 ====================
 */

module.exports = {
  // 认证
  login,
  getUserInfo,
  
  // 闪记
  createFlash,
  getFlashList,
  getFlashDetail,
  updateFlash,
  deleteFlash,
  toggleFavorite,
  getAIStatus,
  
  // 文件上传
  uploadAudio
}

