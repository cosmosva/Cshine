/**
 * 提示工具类
 * 封装微信小程序的提示 API
 */

/**
 * 显示 Toast 提示
 * @param {string} title - 提示文字
 * @param {string} icon - 图标类型（success/error/loading/none）
 * @param {number} duration - 持续时间（毫秒）
 */
function showToast(title, icon = 'none', duration = 2000) {
  wx.showToast({
    title,
    icon,
    duration,
    mask: false
  })
}

/**
 * 显示成功提示
 * @param {string} title - 提示文字
 * @param {number} duration - 持续时间
 */
function showSuccess(title = '操作成功', duration = 1500) {
  showToast(title, 'success', duration)
}

/**
 * 显示错误提示
 * @param {string} title - 提示文字
 * @param {number} duration - 持续时间
 */
function showError(title = '操作失败', duration = 2000) {
  showToast(title, 'error', duration)
}

/**
 * 显示加载中
 * @param {string} title - 提示文字
 * @param {boolean} mask - 是否显示透明蒙层，防止触摸穿透
 */
function showLoading(title = '加载中...', mask = true) {
  wx.showLoading({
    title,
    mask
  })
}

/**
 * 隐藏加载中
 */
function hideLoading() {
  wx.hideLoading()
}

/**
 * 显示确认对话框
 * @param {string} content - 提示内容
 * @param {string} title - 标题
 * @param {Object} options - 其他选项
 * @returns {Promise<boolean>} 用户是否确认
 */
function showConfirm(content, title = '提示', options = {}) {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      confirmText: options.confirmText || '确定',
      cancelText: options.cancelText || '取消',
      confirmColor: options.confirmColor || '#4A6FE8',
      cancelColor: options.cancelColor || '#86868B',
      success: (res) => {
        resolve(res.confirm)
      },
      fail: () => {
        resolve(false)
      }
    })
  })
}

/**
 * 显示操作菜单
 * @param {Array<string>} itemList - 按钮文字数组
 * @returns {Promise<number>} 用户点击的按钮索引（从0开始）
 */
function showActionSheet(itemList) {
  return new Promise((resolve, reject) => {
    wx.showActionSheet({
      itemList,
      success: (res) => {
        resolve(res.tapIndex)
      },
      fail: (err) => {
        if (err.errMsg === 'showActionSheet:fail cancel') {
          reject('cancel')
        } else {
          reject(err)
        }
      }
    })
  })
}

/**
 * 震动反馈
 * @param {string} type - 震动类型（light/medium/heavy）
 */
function vibrateShort(type = 'medium') {
  if (wx.vibrateShort) {
    wx.vibrateShort({ type })
  }
}

/**
 * 长震动
 */
function vibrateLong() {
  if (wx.vibrateLong) {
    wx.vibrateLong()
  }
}

module.exports = {
  showToast,
  showSuccess,
  showError,
  showLoading,
  hideLoading,
  showConfirm,
  showActionSheet,
  vibrateShort,
  vibrateLong
}

