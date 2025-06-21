/**
 * 页面信息缓存管理器
 * 防止切换页面时终端日志任务记录被刷新
 */

class PageCacheManager {
  constructor() {
    this.cache = new Map()
    this.maxCacheSize = 10 // 最多缓存10个页面的数据
    this.cacheTimeout = 5 * 60 * 1000 // 5分钟过期
    
    // 监听页面卸载事件
    window.addEventListener('beforeunload', () => {
      this.saveToStorage()
    })
    
    // 从localStorage恢复缓存
    this.loadFromStorage()
  }
  
  /**
   * 缓存页面数据
   * @param {string} pageKey - 页面标识
   * @param {object} data - 要缓存的数据
   */
  setPageData(pageKey, data) {
    const cacheItem = {
      data: JSON.parse(JSON.stringify(data)), // 深拷贝
      timestamp: Date.now(),
      pageKey
    }
    
    this.cache.set(pageKey, cacheItem)
    
    // 清理过期缓存
    this.cleanExpiredCache()
    
    // 限制缓存大小
    if (this.cache.size > this.maxCacheSize) {
      const oldestKey = this.cache.keys().next().value
      this.cache.delete(oldestKey)
    }
    
    // 保存到localStorage
    this.saveToStorage()
    
    console.log(`📦 页面数据已缓存: ${pageKey}`)
  }
  
  /**
   * 获取页面缓存数据
   * @param {string} pageKey - 页面标识
   * @returns {object|null} 缓存的数据或null
   */
  getPageData(pageKey) {
    const cacheItem = this.cache.get(pageKey)
    
    if (!cacheItem) {
      return null
    }
    
    // 检查是否过期
    if (Date.now() - cacheItem.timestamp > this.cacheTimeout) {
      this.cache.delete(pageKey)
      console.log(`🗑️ 页面缓存已过期: ${pageKey}`)
      return null
    }
    
    console.log(`📋 恢复页面缓存: ${pageKey}`)
    return cacheItem.data
  }
  
  /**
   * 删除页面缓存
   * @param {string} pageKey - 页面标识
   */
  removePageData(pageKey) {
    if (this.cache.has(pageKey)) {
      this.cache.delete(pageKey)
      this.saveToStorage()
      console.log(`🗑️ 页面缓存已删除: ${pageKey}`)
    }
  }
  
  /**
   * 清空所有缓存
   */
  clearAll() {
    this.cache.clear()
    localStorage.removeItem('pageCache')
    console.log('🧹 所有页面缓存已清空')
  }
  
  /**
   * 清理过期缓存
   */
  cleanExpiredCache() {
    const now = Date.now()
    const expiredKeys = []
    
    for (const [key, item] of this.cache.entries()) {
      if (now - item.timestamp > this.cacheTimeout) {
        expiredKeys.push(key)
      }
    }
    
    expiredKeys.forEach(key => {
      this.cache.delete(key)
    })
    
    if (expiredKeys.length > 0) {
      console.log(`🧹 清理了 ${expiredKeys.length} 个过期缓存`)
    }
  }
  
  /**
   * 保存缓存到localStorage
   */
  saveToStorage() {
    try {
      const cacheData = {}
      for (const [key, item] of this.cache.entries()) {
        cacheData[key] = item
      }
      localStorage.setItem('pageCache', JSON.stringify(cacheData))
    } catch (error) {
      console.warn('保存页面缓存到localStorage失败:', error)
    }
  }
  
  /**
   * 从localStorage加载缓存
   */
  loadFromStorage() {
    try {
      const cacheData = localStorage.getItem('pageCache')
      if (cacheData) {
        const parsed = JSON.parse(cacheData)
        const now = Date.now()
        
        for (const [key, item] of Object.entries(parsed)) {
          // 只加载未过期的缓存
          if (now - item.timestamp <= this.cacheTimeout) {
            this.cache.set(key, item)
          }
        }
        
        console.log(`📋 从localStorage恢复了 ${this.cache.size} 个页面缓存`)
      }
    } catch (error) {
      console.warn('从localStorage加载页面缓存失败:', error)
    }
  }
  
  /**
   * 获取缓存统计信息
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      timeout: this.cacheTimeout,
      keys: Array.from(this.cache.keys())
    }
  }
}

// 创建全局实例
const pageCacheManager = new PageCacheManager()

// 页面缓存工具函数
export const pageCache = {
  /**
   * 缓存爬虫任务数据
   */
  cacheSpiderTask(taskId, taskData) {
    const pageKey = `spider_task_${taskId}`
    pageCacheManager.setPageData(pageKey, {
      taskId,
      taskData,
      logs: taskData.logs || [],
      stats: taskData.stats || {},
      timestamp: Date.now()
    })
  },
  
  /**
   * 获取爬虫任务缓存
   */
  getSpiderTask(taskId) {
    const pageKey = `spider_task_${taskId}`
    return pageCacheManager.getPageData(pageKey)
  },

  /**
   * 删除爬虫任务缓存
   */
  removeSpiderTask(taskId) {
    const pageKey = `spider_task_${taskId}`
    pageCacheManager.removePageData(pageKey)
  },
  
  /**
   * 缓存数据管理页面状态
   */
  cacheDataManagement(filters, projects, pagination) {
    pageCacheManager.setPageData('data_management', {
      filters,
      projects,
      pagination,
      timestamp: Date.now()
    })
  },
  
  /**
   * 获取数据管理页面缓存
   */
  getDataManagement() {
    return pageCacheManager.getPageData('data_management')
  },
  
  /**
   * 缓存任务历史页面状态
   */
  cacheTaskHistory(tasks, filters) {
    pageCacheManager.setPageData('task_history', {
      tasks,
      filters,
      timestamp: Date.now()
    })
  },
  
  /**
   * 获取任务历史页面缓存
   */
  getTaskHistory() {
    return pageCacheManager.getPageData('task_history')
  },
  
  /**
   * 清理特定任务的缓存
   */
  clearTaskCache(taskId) {
    const pageKey = `spider_task_${taskId}`
    pageCacheManager.removePageData(pageKey)
  },
  
  /**
   * 清空所有缓存
   */
  clearAll() {
    pageCacheManager.clearAll()
  },
  
  /**
   * 获取缓存统计
   */
  getStats() {
    return pageCacheManager.getCacheStats()
  }
}

export default pageCache
