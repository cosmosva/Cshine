/**
 * 本地存储工具类
 * 封装微信小程序的 Storage API
 */

const STORAGE_PREFIX = 'cshine_' // 存储key前缀

/**
 * 设置存储
 * @param {string} key - 存储键
 * @param {any} value - 存储值
 * @returns {Promise<boolean>} 是否成功
 */
function setStorage(key, value) {
  return new Promise((resolve) => {
    try {
      wx.setStorage({
        key: STORAGE_PREFIX + key,
        data: value,
        success: () => resolve(true),
        fail: () => resolve(false)
      })
    } catch (e) {
      console.error('setStorage error:', e)
      resolve(false)
    }
  })
}

/**
 * 获取存储
 * @param {string} key - 存储键
 * @param {any} defaultValue - 默认值
 * @returns {Promise<any>} 存储的值
 */
function getStorage(key, defaultValue = null) {
  return new Promise((resolve) => {
    try {
      wx.getStorage({
        key: STORAGE_PREFIX + key,
        success: (res) => resolve(res.data),
        fail: () => resolve(defaultValue)
      })
    } catch (e) {
      console.error('getStorage error:', e)
      resolve(defaultValue)
    }
  })
}

/**
 * 同步设置存储
 * @param {string} key - 存储键
 * @param {any} value - 存储值
 * @returns {boolean} 是否成功
 */
function setStorageSync(key, value) {
  try {
    wx.setStorageSync(STORAGE_PREFIX + key, value)
    return true
  } catch (e) {
    console.error('setStorageSync error:', e)
    return false
  }
}

/**
 * 同步获取存储
 * @param {string} key - 存储键
 * @param {any} defaultValue - 默认值
 * @returns {any} 存储的值
 */
function getStorageSync(key, defaultValue = null) {
  try {
    const value = wx.getStorageSync(STORAGE_PREFIX + key)
    return value !== '' ? value : defaultValue
  } catch (e) {
    console.error('getStorageSync error:', e)
    return defaultValue
  }
}

/**
 * 删除存储
 * @param {string} key - 存储键
 * @returns {Promise<boolean>} 是否成功
 */
function removeStorage(key) {
  return new Promise((resolve) => {
    try {
      wx.removeStorage({
        key: STORAGE_PREFIX + key,
        success: () => resolve(true),
        fail: () => resolve(false)
      })
    } catch (e) {
      console.error('removeStorage error:', e)
      resolve(false)
    }
  })
}

/**
 * 清空所有存储（仅清空带前缀的）
 * @returns {Promise<boolean>} 是否成功
 */
function clearStorage() {
  return new Promise((resolve) => {
    try {
      wx.getStorageInfo({
        success: (res) => {
          const keys = res.keys.filter(k => k.startsWith(STORAGE_PREFIX))
          const promises = keys.map(k => 
            new Promise(r => wx.removeStorage({ key: k, complete: () => r() }))
          )
          Promise.all(promises).then(() => resolve(true))
        },
        fail: () => resolve(false)
      })
    } catch (e) {
      console.error('clearStorage error:', e)
      resolve(false)
    }
  })
}

// 常用存储键
const StorageKeys = {
  USER_INFO: 'user_info',         // 用户信息
  TOKEN: 'token',                 // 登录token
  FLASH_HISTORY: 'flash_history', // 闪记历史（本地缓存）
  SETTINGS: 'settings',           // 用户设置
  LAST_SYNC_TIME: 'last_sync_time' // 最后同步时间
}

module.exports = {
  setStorage,
  getStorage,
  setStorageSync,
  getStorageSync,
  removeStorage,
  clearStorage,
  StorageKeys
}

