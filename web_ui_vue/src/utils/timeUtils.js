/**
 * 时间工具函数
 * 统一处理时区显示问题，确保显示北京时间（GMT+8）
 */

import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

// 扩展dayjs插件
dayjs.extend(utc)
dayjs.extend(timezone)

// 设置默认时区为北京时间
const BEIJING_TIMEZONE = 'Asia/Shanghai'

/**
 * 格式化日期时间为本地时间
 * @param {string} dateStr - 日期字符串
 * @param {string} format - 格式化模板，默认为 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的时间字符串
 */
export function formatDateTime(dateStr, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!dateStr) return ''
  
  try {
    // 使用dayjs处理时区转换
    return dayjs(dateStr).tz(BEIJING_TIMEZONE).format(format)
  } catch (error) {
    console.warn('时间格式化失败:', dateStr, error)
    return dateStr
  }
}

/**
 * 格式化日期（不包含时间）
 * @param {string} dateStr - 日期字符串
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(dateStr) {
  return formatDateTime(dateStr, 'YYYY-MM-DD')
}

/**
 * 格式化时间（不包含日期）
 * @param {string} dateStr - 日期字符串
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(dateStr) {
  return formatDateTime(dateStr, 'HH:mm:ss')
}

/**
 * 格式化为相对时间（多少分钟前、小时前等）
 * @param {string} dateStr - 日期字符串
 * @returns {string} 相对时间字符串
 */
export function formatRelativeTime(dateStr) {
  if (!dateStr) return ''
  
  try {
    const date = dayjs(dateStr).tz(BEIJING_TIMEZONE)
    const now = dayjs().tz(BEIJING_TIMEZONE)
    const diffMs = now.diff(date)
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)
    
    if (diffMins < 1) return '刚刚'
    if (diffMins < 60) return `${diffMins}分钟前`
    if (diffHours < 24) return `${diffHours}小时前`
    if (diffDays < 7) return `${diffDays}天前`
    
    return formatDate(dateStr)
  } catch (error) {
    console.warn('相对时间格式化失败:', dateStr, error)
    return dateStr
  }
}

/**
 * 获取当前北京时间
 * @param {string} format - 格式化模板
 * @returns {string} 当前时间字符串
 */
export function getCurrentTime(format = 'YYYY-MM-DD HH:mm:ss') {
  return dayjs().tz(BEIJING_TIMEZONE).format(format)
}

/**
 * 检查时间字符串是否有效
 * @param {string} dateStr - 日期字符串
 * @returns {boolean} 是否有效
 */
export function isValidDateTime(dateStr) {
  if (!dateStr) return false
  return dayjs(dateStr).isValid()
}

/**
 * 转换UTC时间为北京时间
 * @param {string} utcDateStr - UTC时间字符串
 * @param {string} format - 格式化模板
 * @returns {string} 北京时间字符串
 */
export function utcToBeijing(utcDateStr, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!utcDateStr) return ''
  
  try {
    return dayjs.utc(utcDateStr).tz(BEIJING_TIMEZONE).format(format)
  } catch (error) {
    console.warn('UTC时间转换失败:', utcDateStr, error)
    return utcDateStr
  }
}

/**
 * 转换北京时间为UTC时间
 * @param {string} beijingDateStr - 北京时间字符串
 * @param {string} format - 格式化模板
 * @returns {string} UTC时间字符串
 */
export function beijingToUtc(beijingDateStr, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!beijingDateStr) return ''
  
  try {
    return dayjs.tz(beijingDateStr, BEIJING_TIMEZONE).utc().format(format)
  } catch (error) {
    console.warn('北京时间转换失败:', beijingDateStr, error)
    return beijingDateStr
  }
}

/**
 * 使用浏览器原生API格式化时间（兼容性更好）
 * @param {string} dateStr - 日期字符串
 * @param {object} options - 格式化选项
 * @returns {string} 格式化后的时间字符串
 */
export function formatDateTimeNative(dateStr, options = {}) {
  if (!dateStr) return ''
  
  try {
    const date = new Date(dateStr)
    const defaultOptions = {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: BEIJING_TIMEZONE,
      hour12: false
    }
    
    return date.toLocaleString('zh-CN', { ...defaultOptions, ...options })
  } catch (error) {
    console.warn('原生时间格式化失败:', dateStr, error)
    return dateStr
  }
}

// 导出默认配置
export const TIME_CONFIG = {
  timezone: BEIJING_TIMEZONE,
  defaultFormat: 'YYYY-MM-DD HH:mm:ss',
  dateFormat: 'YYYY-MM-DD',
  timeFormat: 'HH:mm:ss'
}
