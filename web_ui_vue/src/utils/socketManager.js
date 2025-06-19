/**
 * 增强的WebSocket连接管理器
 * 提供稳定的连接和重连机制
 */

import { io } from 'socket.io-client'

class SocketManager {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 1000 // 初始重连延迟1秒
    this.maxReconnectDelay = 30000 // 最大重连延迟30秒
    this.heartbeatInterval = null
    this.heartbeatTimeout = 30000 // 30秒心跳超时
    
    // 事件监听器
    this.listeners = new Map()
    
    // 连接状态回调
    this.onConnectionChange = null
    
    // 自动连接
    this.connect()
  }
  
  /**
   * 建立WebSocket连接
   */
  connect() {
    if (this.socket && this.socket.connected) {
      console.log('🔌 WebSocket已连接，跳过重复连接')
      return
    }
    
    console.log('🔌 正在建立WebSocket连接...')
    
    // 创建socket连接
    this.socket = io({
      transports: ['websocket', 'polling'],
      upgrade: true,
      rememberUpgrade: true,
      timeout: 20000,
      forceNew: true,
      reconnection: false, // 我们自己处理重连
      autoConnect: true
    })
    
    this.setupEventListeners()
  }
  
  /**
   * 设置事件监听器
   */
  setupEventListeners() {
    if (!this.socket) return
    
    // 连接成功
    this.socket.on('connect', () => {
      console.log('✅ WebSocket连接成功')
      this.isConnected = true
      this.reconnectAttempts = 0
      this.reconnectDelay = 1000
      
      // 启动心跳检测
      this.startHeartbeat()
      
      // 通知连接状态变化
      if (this.onConnectionChange) {
        this.onConnectionChange(true)
      }
      
      // 重新注册所有监听器
      this.reregisterListeners()
    })
    
    // 连接断开
    this.socket.on('disconnect', (reason) => {
      console.log('🔌 WebSocket连接断开:', reason)
      this.isConnected = false
      
      // 停止心跳检测
      this.stopHeartbeat()
      
      // 通知连接状态变化
      if (this.onConnectionChange) {
        this.onConnectionChange(false)
      }
      
      // 自动重连（除非是主动断开）
      if (reason !== 'io client disconnect') {
        this.scheduleReconnect()
      }
    })
    
    // 连接错误
    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket连接错误:', error)
      this.isConnected = false
      
      // 通知连接状态变化
      if (this.onConnectionChange) {
        this.onConnectionChange(false)
      }
      
      this.scheduleReconnect()
    })
    
    // 心跳响应
    this.socket.on('pong', (data) => {
      console.log('💓 收到心跳响应:', data)
    })
  }
  
  /**
   * 启动心跳检测
   */
  startHeartbeat() {
    this.stopHeartbeat() // 先停止之前的心跳
    
    this.heartbeatInterval = setInterval(() => {
      if (this.socket && this.socket.connected) {
        console.log('💓 发送心跳检测')
        this.socket.emit('ping')
      }
    }, this.heartbeatTimeout)
  }
  
  /**
   * 停止心跳检测
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }
  
  /**
   * 安排重连
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ 达到最大重连次数，停止重连')
      return
    }
    
    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay)
    
    console.log(`🔄 ${delay/1000}秒后尝试第${this.reconnectAttempts}次重连...`)
    
    setTimeout(() => {
      if (!this.isConnected) {
        this.connect()
      }
    }, delay)
  }
  
  /**
   * 重新注册所有监听器
   */
  reregisterListeners() {
    for (const [event, callbacks] of this.listeners.entries()) {
      for (const callback of callbacks) {
        this.socket.on(event, callback)
      }
    }
    console.log(`🔄 重新注册了 ${this.listeners.size} 个事件监听器`)
  }
  
  /**
   * 添加事件监听器
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)
    
    // 如果socket已连接，立即注册
    if (this.socket && this.socket.connected) {
      this.socket.on(event, callback)
    }
  }
  
  /**
   * 移除事件监听器
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
      
      // 如果没有更多监听器，删除事件
      if (this.listeners.get(event).size === 0) {
        this.listeners.delete(event)
      }
    }
    
    // 从socket移除监听器
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }
  
  /**
   * 发送消息
   */
  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data)
      return true
    } else {
      console.warn('⚠️ WebSocket未连接，无法发送消息:', event)
      return false
    }
  }
  
  /**
   * 手动重连
   */
  reconnect() {
    console.log('🔄 手动触发重连...')
    this.disconnect()
    setTimeout(() => {
      this.connect()
    }, 1000)
  }
  
  /**
   * 断开连接
   */
  disconnect() {
    console.log('🔌 主动断开WebSocket连接')
    this.isConnected = false
    this.stopHeartbeat()
    
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }
  
  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      maxReconnectAttempts: this.maxReconnectAttempts,
      listenersCount: this.listeners.size,
      socketId: this.socket?.id || null
    }
  }
  
  /**
   * 设置连接状态变化回调
   */
  setConnectionChangeCallback(callback) {
    this.onConnectionChange = callback
  }
}

// 创建全局实例
const socketManager = new SocketManager()

export default socketManager
