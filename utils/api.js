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
  // 不使用 showLoad，由调用方控制 loading 状态
  return upload(API_ENDPOINTS.UPLOAD_AUDIO, filePath, {}, { showLoad: false })
}

/**
 * 获取 OSS 上传签名
 */
function getOssSignature() {
  return get(API_ENDPOINTS.UPLOAD_OSS_SIGNATURE || '/api/v1/upload/oss-signature')
}

/**
 * ==================== 知识库（文件夹）相关 ====================
 */

/**
 * 创建知识库
 * @param {object} data 知识库数据 { name: '知识库名称' }
 */
function createFolder(data) {
  return post(API_ENDPOINTS.FOLDER_CREATE || '/api/v1/folders', data)
}

/**
 * 获取知识库列表
 */
function getFolders() {
  return get(API_ENDPOINTS.FOLDER_LIST || '/api/v1/folders')
}

/**
 * 更新知识库
 * @param {number} folderId 知识库ID
 * @param {object} data 更新的数据
 */
function updateFolder(folderId, data) {
  return put((API_ENDPOINTS.FOLDER_UPDATE || '/api/v1/folders/') + folderId, data)
}

/**
 * 删除知识库
 * @param {number} folderId 知识库ID
 */
function deleteFolder(folderId) {
  return del((API_ENDPOINTS.FOLDER_DELETE || '/api/v1/folders/') + folderId)
}


/**
 * ==================== 会议纪要相关 ====================
 */

/**
 * 创建会议纪要
 * @param {object} data 会议数据
 */
function createMeeting(data) {
  // 不使用 showLoad，由调用方控制 loading 状态
  return post(API_ENDPOINTS.MEETING_CREATE, data, { showLoad: false })
}

/**
 * 获取会议纪要列表
 * @param {object} params 查询参数
 */
function getMeetingList(params = {}) {
  const defaultParams = {
    page: 1,
    page_size: 20
  }
  return get(API_ENDPOINTS.MEETING_LIST, { ...defaultParams, ...params })
}

/**
 * 获取会议纪要详情
 * @param {string} meetingId 会议ID
 */
function getMeetingDetail(meetingId) {
  return get(API_ENDPOINTS.MEETING_DETAIL + meetingId)
}

/**
 * 更新会议纪要
 * @param {string} meetingId 会议ID
 * @param {object} data 更新的数据
 */
function updateMeeting(meetingId, data) {
  return put(API_ENDPOINTS.MEETING_UPDATE + meetingId, data)
}

/**
 * 复制会议纪要
 * @param {string} meetingId 会议ID
 * @param {object} data 复制配置 { folder_id: number | null }
 */
function copyMeeting(meetingId, data) {
  return post(`/api/v1/meeting/${meetingId}/copy`, data)
}

/**
 * 删除会议纪要
 * @param {string} meetingId 会议ID
 */
function deleteMeeting(meetingId) {
  return del(API_ENDPOINTS.MEETING_DELETE + meetingId)
}

/**
 * 查询会议处理状态
 * @param {string} meetingId 会议ID
 */
function getMeetingStatus(meetingId) {
  return get(API_ENDPOINTS.MEETING_STATUS + meetingId + '/status')
}

/**
 * 切换会议收藏状态
 * @param {string} meetingId 会议ID
 */
function toggleMeetingFavorite(meetingId) {
  return put(API_ENDPOINTS.MEETING_UPDATE + meetingId + '/favorite')
}

/**
 * ==================== 联系人相关 ====================
 */

/**
 * 创建联系人
 * @param {object} data 联系人数据
 */
function createContact(data) {
  return post(API_ENDPOINTS.CONTACT_CREATE, data, { showLoad: true })
}

/**
 * 获取联系人列表
 */
function getContacts() {
  return get(API_ENDPOINTS.CONTACT_LIST)
}

/**
 * 获取联系人详情
 * @param {number} contactId 联系人ID
 */
function getContactDetail(contactId) {
  return get(`${API_ENDPOINTS.CONTACT_DETAIL}/${contactId}`)
}

/**
 * 更新联系人
 * @param {number} contactId 联系人ID
 * @param {object} data 更新数据
 */
function updateContact(contactId, data) {
  return put(`${API_ENDPOINTS.CONTACT_UPDATE}/${contactId}`, data, { showLoad: true })
}

/**
 * 删除联系人
 * @param {number} contactId 联系人ID
 */
function deleteContact(contactId) {
  return del(`${API_ENDPOINTS.CONTACT_DELETE}/${contactId}`, {}, { showLoad: true })
}

/**
 * ==================== 说话人标注相关 ====================
 */

/**
 * 标注会议说话人
 * @param {string} meetingId 会议ID
 * @param {object} data { speaker_id, contact_id, custom_name }
 */
function mapSpeaker(meetingId, data) {
  return post(`${API_ENDPOINTS.MEETING_DETAIL}${meetingId}/speakers/map`, data, { showLoad: true })
}

/**
 * 获取会议说话人映射
 * @param {string} meetingId 会议ID
 */
function getMeetingSpeakers(meetingId) {
  return get(`${API_ENDPOINTS.MEETING_DETAIL}${meetingId}/speakers`)
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
  
  // 会议纪要
  createMeeting,
  getMeetingList,
  getMeetingDetail,
  updateMeeting,
  copyMeeting,
  deleteMeeting,
  getMeetingStatus,
  toggleMeetingFavorite,
  
  // 文件上传
  uploadAudio,
  getOssSignature,
  
  // 知识库
  createFolder,
  getFolders,
  updateFolder,
  deleteFolder,
  
  // 联系人
  createContact,
  getContacts,
  getContactDetail,
  updateContact,
  deleteContact,
  
  // 说话人标注
  mapSpeaker,
  getMeetingSpeakers
}

