/**
 * 格式化工具类
 */

/**
 * 格式化时间（UTC+8时区）
 * @param {Date|string|number} time - 时间（UTC时间）
 * @param {string} format - 格式（默认 'YYYY-MM-DD HH:mm:ss'）
 * @returns {string} 格式化后的时间字符串（UTC+8）
 */
function formatTime(time, format = 'YYYY-MM-DD HH:mm:ss') {
  let date = time instanceof Date ? time : new Date(time)

  if (isNaN(date.getTime())) {
    return ''
  }

  // 转换为 UTC+8 时区（中国标准时间）
  // getTime() 返回 UTC 时间戳，加上 8 小时的毫秒数
  const utc8Offset = 8 * 60 * 60 * 1000  // 8小时的毫秒数
  const utc8Time = date.getTime() + utc8Offset
  date = new Date(utc8Time)

  const year = date.getUTCFullYear()
  const month = String(date.getUTCMonth() + 1).padStart(2, '0')
  const day = String(date.getUTCDate()).padStart(2, '0')
  const hours = String(date.getUTCHours()).padStart(2, '0')
  const minutes = String(date.getUTCMinutes()).padStart(2, '0')
  const seconds = String(date.getUTCSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期时间（formatTime 的别名）
 * @param {Date|string|number} time - 时间
 * @param {string} format - 格式
 * @returns {string} 格式化后的时间字符串
 */
function formatDateTime(time, format) {
  return formatTime(time, format)
}

/**
 * 格式化相对时间（刚刚、5分钟前、昨天等）
 * @param {Date|string|number} time - 时间
 * @returns {string} 相对时间描述
 */
function formatRelativeTime(time) {
  const date = time instanceof Date ? time : new Date(time)
  const now = new Date()
  const diff = now - date // 毫秒差
  
  // 少于1分钟
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 少于1小时
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}分钟前`
  }
  
  // 少于1天
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}小时前`
  }
  
  // 昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === yesterday.toDateString()) {
    return '昨天 ' + formatTime(date, 'HH:mm')
  }
  
  // 今年内
  if (date.getFullYear() === now.getFullYear()) {
    return formatTime(date, 'MM-DD HH:mm')
  }
  
  // 往年
  return formatTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化音频时长
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时长（如 "1:23" 或 "12:34"）
 */
function formatDuration(seconds) {
  if (!seconds || seconds < 0) return '0:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${String(secs).padStart(2, '0')}`
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 格式化数字（添加千分位）
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字
 */
function formatNumber(num) {
  return String(num).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

/**
 * 截取文本（超出显示省略号）
 * @param {string} text - 文本
 * @param {number} maxLength - 最大长度
 * @returns {string} 截取后的文本
 */
function truncateText(text, maxLength = 50) {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

module.exports = {
  formatTime,
  formatDateTime,
  formatRelativeTime,
  formatDuration,
  formatFileSize,
  formatNumber,
  truncateText
}

