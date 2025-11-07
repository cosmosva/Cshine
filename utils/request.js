/**
 * 网络请求封装
 * 统一处理请求、响应、错误、Token 等
 */

const { API_BASE_URL, STORAGE_KEYS } = require('./config')
const { showError, showLoading, hideLoading } = require('./toast')

/**
 * 发起请求
 * @param {Object} options 请求配置
 * @returns {Promise} 返回 Promise
 */
function request(options) {
  const {
    url,
    method = 'GET',
    data = {},
    header = {},
    needAuth = true,
    showLoad = false,
    loadingText = '加载中...'
  } = options

  // 显示加载提示
  if (showLoad) {
    showLoading(loadingText)
  }

  // 获取 Token
  let token = ''
  if (needAuth) {
    token = wx.getStorageSync(STORAGE_KEYS.TOKEN)
    if (!token) {
      console.warn('未找到 Token，可能需要重新登录')
    }
  }

  // 构建完整 URL
  const fullUrl = API_BASE_URL + url

  // 构建请求头
  const requestHeader = {
    'Content-Type': 'application/json',
    ...header
  }

  // 添加 Authorization
  if (needAuth && token) {
    requestHeader['Authorization'] = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method,
      data,
      header: requestHeader,
      success: (res) => {
        console.log(`[API] ${method} ${url}`, res)

        // 隐藏加载提示
        if (showLoad) {
          hideLoading()
        }

        // 处理响应
        if (res.statusCode === 200) {
          // 统一响应格式
          if (res.data && res.data.code === 200) {
            resolve(res.data.data)
          } else {
            // 业务错误
            const errorMsg = res.data.message || '请求失败'
            showError(errorMsg)
            reject(new Error(errorMsg))
          }
        } else if (res.statusCode === 401) {
          // Token 失效，清除并跳转登录
          console.warn('Token 失效，需要重新登录')
          wx.removeStorageSync(STORAGE_KEYS.TOKEN)
          wx.removeStorageSync(STORAGE_KEYS.USER_INFO)
          showError('登录已过期，请重新登录')
          reject(new Error('Unauthorized'))
        } else if (res.statusCode === 404) {
          showError('请求的资源不存在')
          reject(new Error('Not Found'))
        } else if (res.statusCode === 422) {
          // 参数验证错误
          const errorMsg = res.data.detail || '参数错误'
          showError(errorMsg)
          reject(new Error(errorMsg))
        } else {
          // 其他错误
          const errorMsg = res.data.detail || `请求失败 (${res.statusCode})`
          showError(errorMsg)
          reject(new Error(errorMsg))
        }
      },
      fail: (err) => {
        console.error(`[API Error] ${method} ${url}`, err)
        
        // 隐藏加载提示
        if (showLoad) {
          hideLoading()
        }

        // 网络错误
        if (err.errMsg.includes('timeout')) {
          showError('请求超时，请稍后重试')
        } else if (err.errMsg.includes('fail')) {
          showError('网络连接失败，请检查网络')
        } else {
          showError('请求失败，请重试')
        }
        
        reject(err)
      }
    })
  })
}

/**
 * GET 请求
 */
function get(url, params = {}, options = {}) {
  // 构建查询字符串
  const queryString = Object.keys(params)
    .filter(key => params[key] !== undefined && params[key] !== null)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')
  
  const fullUrl = queryString ? `${url}?${queryString}` : url

  return request({
    url: fullUrl,
    method: 'GET',
    ...options
  })
}

/**
 * POST 请求
 */
function post(url, data = {}, options = {}) {
  return request({
    url,
    method: 'POST',
    data,
    ...options
  })
}

/**
 * PUT 请求
 */
function put(url, data = {}, options = {}) {
  return request({
    url,
    method: 'PUT',
    data,
    ...options
  })
}

/**
 * DELETE 请求
 */
function del(url, options = {}) {
  return request({
    url,
    method: 'DELETE',
    ...options
  })
}

/**
 * 上传文件
 */
function upload(url, filePath, formData = {}, options = {}) {
  const { needAuth = true, showLoad = false } = options

  if (showLoad) {
    showLoading('上传中...')
  }

  // 获取 Token
  let token = ''
  if (needAuth) {
    token = wx.getStorageSync(STORAGE_KEYS.TOKEN)
  }

  const fullUrl = API_BASE_URL + url

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: fullUrl,
      filePath,
      name: 'file',
      formData,
      header: needAuth && token ? {
        'Authorization': `Bearer ${token}`
      } : {},
      success: (res) => {
        if (showLoad) {
          hideLoading()
        }

        const data = JSON.parse(res.data)
        if (data.code === 200) {
          resolve(data.data)
        } else {
          showError(data.message || '上传失败')
          reject(new Error(data.message))
        }
      },
      fail: (err) => {
        if (showLoad) {
          hideLoading()
        }
        showError('上传失败，请重试')
        reject(err)
      }
    })
  })
}

module.exports = {
  request,
  get,
  post,
  put,
  del,
  upload
}

