/**
 * 图片URL验证和处理工具
 */

/**
 * 验证图片URL是否有效
 * @param {string} url - 图片URL
 * @returns {boolean} - 是否有效
 */
export function isValidImageUrl(url) {
  if (!url || typeof url !== 'string') return false
  
  // 排除明显无效的值
  const invalidValues = ['none', 'null', 'undefined', '', ' ', 'N/A', 'n/a']
  if (invalidValues.includes(url.toLowerCase().trim())) return false
  
  // 检查是否是有效的URL格式
  try {
    const urlObj = new URL(url, window.location.origin)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:' || urlObj.protocol === 'data:'
  } catch {
    return false
  }
}

/**
 * 获取安全的图片URL，如果无效则返回默认图片
 * @param {string} url - 原始图片URL
 * @param {string} fallback - 默认图片URL
 * @returns {string} - 安全的图片URL
 */
export function getSafeImageUrl(url, fallback = '/placeholder-image.jpg') {
  return isValidImageUrl(url) ? url : fallback
}

/**
 * 获取安全的头像URL，如果无效则返回默认头像
 * @param {string} url - 原始头像URL
 * @returns {string} - 安全的头像URL
 */
export function getSafeAvatarUrl(url) {
  return getSafeImageUrl(url, '/placeholder-avatar.jpg')
}

/**
 * 预加载图片并返回Promise
 * @param {string} url - 图片URL
 * @returns {Promise} - 加载结果
 */
export function preloadImage(url) {
  return new Promise((resolve, reject) => {
    if (!isValidImageUrl(url)) {
      reject(new Error('Invalid image URL'))
      return
    }
    
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error('Failed to load image'))
    img.src = url
  })
}

/**
 * 检查图片是否可以加载
 * @param {string} url - 图片URL
 * @returns {Promise<boolean>} - 是否可以加载
 */
export async function canLoadImage(url) {
  try {
    await preloadImage(url)
    return true
  } catch {
    return false
  }
}
