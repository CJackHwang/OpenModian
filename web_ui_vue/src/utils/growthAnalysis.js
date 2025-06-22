/**
 * 增长率分析工具函数
 * 用于计算不同时间周期的增长率和趋势分析
 */

// 使用原生Date对象，避免dayjs依赖问题

/**
 * 计算两个值之间的增长率
 * @param {number} currentValue - 当前值
 * @param {number} previousValue - 之前的值
 * @returns {number} 增长率百分比
 */
export function calculateGrowthRate(currentValue, previousValue) {
  if (!previousValue || previousValue === 0) {
    return currentValue > 0 ? 100 : 0
  }
  
  const change = currentValue - previousValue
  return (change / previousValue) * 100
}

/**
 * 计算日增长率
 * @param {Array} historyData - 历史数据数组
 * @param {string} field - 要分析的字段名
 * @returns {Object} 日增长率分析结果
 */
export function calculateDailyGrowth(historyData, field) {
  if (!historyData || historyData.length < 2) {
    return { rate: 0, trend: 'stable', data: [] }
  }
  
  // 按日期分组数据
  const dailyData = groupDataByDay(historyData, field)
  const dailyGrowthRates = []
  
  for (let i = 1; i < dailyData.length; i++) {
    const current = dailyData[i]
    const previous = dailyData[i - 1]
    const rate = calculateGrowthRate(current.value, previous.value)
    
    dailyGrowthRates.push({
      date: current.date,
      value: current.value,
      previousValue: previous.value,
      rate: rate,
      change: current.value - previous.value
    })
  }
  
  // 计算平均日增长率
  const avgRate = dailyGrowthRates.length > 0 
    ? dailyGrowthRates.reduce((sum, item) => sum + item.rate, 0) / dailyGrowthRates.length
    : 0
  
  return {
    rate: avgRate,
    trend: getTrend(avgRate),
    data: dailyGrowthRates,
    latest: dailyGrowthRates[dailyGrowthRates.length - 1] || null
  }
}

/**
 * 计算周增长率
 * @param {Array} historyData - 历史数据数组
 * @param {string} field - 要分析的字段名
 * @returns {Object} 周增长率分析结果
 */
export function calculateWeeklyGrowth(historyData, field) {
  if (!historyData || historyData.length < 2) {
    return { rate: 0, trend: 'stable', data: [] }
  }
  
  // 按周分组数据
  const weeklyData = groupDataByWeek(historyData, field)
  const weeklyGrowthRates = []
  
  for (let i = 1; i < weeklyData.length; i++) {
    const current = weeklyData[i]
    const previous = weeklyData[i - 1]
    const rate = calculateGrowthRate(current.value, previous.value)
    
    weeklyGrowthRates.push({
      week: current.week,
      value: current.value,
      previousValue: previous.value,
      rate: rate,
      change: current.value - previous.value
    })
  }
  
  // 计算平均周增长率
  const avgRate = weeklyGrowthRates.length > 0 
    ? weeklyGrowthRates.reduce((sum, item) => sum + item.rate, 0) / weeklyGrowthRates.length
    : 0
  
  return {
    rate: avgRate,
    trend: getTrend(avgRate),
    data: weeklyGrowthRates,
    latest: weeklyGrowthRates[weeklyGrowthRates.length - 1] || null
  }
}

/**
 * 计算月增长率
 * @param {Array} historyData - 历史数据数组
 * @param {string} field - 要分析的字段名
 * @returns {Object} 月增长率分析结果
 */
export function calculateMonthlyGrowth(historyData, field) {
  if (!historyData || historyData.length < 2) {
    return { rate: 0, trend: 'stable', data: [] }
  }
  
  // 按月分组数据
  const monthlyData = groupDataByMonth(historyData, field)
  const monthlyGrowthRates = []
  
  for (let i = 1; i < monthlyData.length; i++) {
    const current = monthlyData[i]
    const previous = monthlyData[i - 1]
    const rate = calculateGrowthRate(current.value, previous.value)
    
    monthlyGrowthRates.push({
      month: current.month,
      value: current.value,
      previousValue: previous.value,
      rate: rate,
      change: current.value - previous.value
    })
  }
  
  // 计算平均月增长率
  const avgRate = monthlyGrowthRates.length > 0 
    ? monthlyGrowthRates.reduce((sum, item) => sum + item.rate, 0) / monthlyGrowthRates.length
    : 0
  
  return {
    rate: avgRate,
    trend: getTrend(avgRate),
    data: monthlyGrowthRates,
    latest: monthlyGrowthRates[monthlyGrowthRates.length - 1] || null
  }
}

/**
 * 按日期分组数据
 * @param {Array} historyData - 历史数据
 * @param {string} field - 字段名
 * @returns {Array} 按日分组的数据
 */
function groupDataByDay(historyData, field) {
  const grouped = {}

  historyData.forEach(item => {
    const date = new Date(item.crawl_time).toISOString().split('T')[0] // YYYY-MM-DD
    if (!grouped[date] || new Date(item.crawl_time) > new Date(grouped[date].crawl_time)) {
      grouped[date] = {
        date,
        value: item[field] || 0,
        crawl_time: item.crawl_time
      }
    }
  })

  return Object.values(grouped).sort((a, b) => new Date(a.date) - new Date(b.date))
}

/**
 * 按周分组数据
 * @param {Array} historyData - 历史数据
 * @param {string} field - 字段名
 * @returns {Array} 按周分组的数据
 */
function groupDataByWeek(historyData, field) {
  const grouped = {}

  historyData.forEach(item => {
    const date = new Date(item.crawl_time)
    const year = date.getFullYear()
    const week = getWeekNumber(date)
    const weekKey = `${year}-W${week.toString().padStart(2, '0')}`

    if (!grouped[weekKey] || new Date(item.crawl_time) > new Date(grouped[weekKey].crawl_time)) {
      grouped[weekKey] = {
        week: weekKey,
        value: item[field] || 0,
        crawl_time: item.crawl_time
      }
    }
  })

  return Object.values(grouped).sort((a, b) => new Date(a.crawl_time) - new Date(b.crawl_time))
}

// 获取周数的辅助函数
function getWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil((((d - yearStart) / 86400000) + 1) / 7)
}

/**
 * 按月分组数据
 * @param {Array} historyData - 历史数据
 * @param {string} field - 字段名
 * @returns {Array} 按月分组的数据
 */
function groupDataByMonth(historyData, field) {
  const grouped = {}

  historyData.forEach(item => {
    const date = new Date(item.crawl_time)
    const month = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`

    if (!grouped[month] || new Date(item.crawl_time) > new Date(grouped[month].crawl_time)) {
      grouped[month] = {
        month,
        value: item[field] || 0,
        crawl_time: item.crawl_time
      }
    }
  })

  return Object.values(grouped).sort((a, b) => new Date(a.crawl_time) - new Date(b.crawl_time))
}

/**
 * 根据增长率确定趋势
 * @param {number} rate - 增长率
 * @returns {string} 趋势类型
 */
function getTrend(rate) {
  if (rate > 5) return 'rising'
  if (rate < -5) return 'falling'
  return 'stable'
}

/**
 * 获取趋势的中文描述
 * @param {string} trend - 趋势类型
 * @returns {string} 中文描述
 */
export function getTrendDescription(trend) {
  const descriptions = {
    rising: '上升趋势',
    falling: '下降趋势',
    stable: '稳定趋势'
  }
  return descriptions[trend] || '未知趋势'
}

/**
 * 获取趋势的颜色类
 * @param {string} trend - 趋势类型
 * @returns {string} CSS颜色类
 */
export function getTrendColorClass(trend) {
  const colorClasses = {
    rising: 'text-success',
    falling: 'text-error',
    stable: 'text-on-surface-variant'
  }
  return colorClasses[trend] || 'text-on-surface-variant'
}

/**
 * 格式化增长率显示
 * @param {number} rate - 增长率
 * @param {number} precision - 小数位数
 * @returns {string} 格式化后的增长率字符串
 */
export function formatGrowthRate(rate, precision = 1) {
  if (rate === undefined || rate === null || isNaN(rate)) return '0%'
  const sign = rate >= 0 ? '+' : ''
  return `${sign}${rate.toFixed(precision)}%`
}
