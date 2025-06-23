import { ref, reactive } from "vue";
import { useSnackbar } from "./useSnackbar";

/**
 * 错误处理组合式函数
 * 提供统一的错误处理、日志记录和用户反馈
 */
export function useErrorHandler() {
  const { showSnackbar } = useSnackbar();

  const errors = ref([]);
  const errorStats = reactive({
    total: 0,
    network: 0,
    validation: 0,
    system: 0,
    unknown: 0,
  });

  // 错误类型枚举
  const ErrorTypes = {
    NETWORK: "network",
    VALIDATION: "validation",
    SYSTEM: "system",
    UNKNOWN: "unknown",
  };

  // 错误严重级别
  const ErrorLevels = {
    LOW: "low",
    MEDIUM: "medium",
    HIGH: "high",
    CRITICAL: "critical",
  };

  /**
   * 处理错误
   * @param {Error|string} error - 错误对象或错误消息
   * @param {Object} options - 选项
   */
  const handleError = (error, options = {}) => {
    const {
      type = ErrorTypes.UNKNOWN,
      level = ErrorLevels.MEDIUM,
      showToUser = true,
      logToConsole = true,
      context = {},
      customMessage = null,
    } = options;

    // 创建标准化错误对象
    const standardError = createStandardError(error, type, level, context);

    // 记录错误
    recordError(standardError);

    // 控制台日志
    if (logToConsole) {
      logError(standardError);
    }

    // 用户反馈
    if (showToUser) {
      showErrorToUser(standardError, customMessage);
    }

    // 上报错误（如果配置了错误监控服务）
    reportError(standardError);

    return standardError;
  };

  /**
   * 创建标准化错误对象
   */
  const createStandardError = (error, type, level, context) => {
    const timestamp = new Date().toISOString();
    const id = generateErrorId();

    let message, stack, code;

    if (error instanceof Error) {
      message = error.message;
      stack = error.stack;
      code = error.code;
    } else if (typeof error === "string") {
      message = error;
      stack = new Error().stack;
    } else {
      message = "未知错误";
      stack = new Error().stack;
    }

    return {
      id,
      message,
      stack,
      code,
      type,
      level,
      timestamp,
      context,
      url: window.location.href,
      userAgent: navigator.userAgent,
    };
  };

  /**
   * 记录错误到本地存储
   */
  const recordError = (error) => {
    errors.value.unshift(error);

    // 限制错误记录数量
    if (errors.value.length > 100) {
      errors.value = errors.value.slice(0, 100);
    }

    // 更新统计
    errorStats.total++;
    errorStats[error.type]++;

    // 持久化到localStorage
    try {
      const errorLog = JSON.parse(localStorage.getItem("errorLog") || "[]");
      errorLog.unshift(error);
      localStorage.setItem("errorLog", JSON.stringify(errorLog.slice(0, 50)));
    } catch (e) {
      console.warn("无法保存错误日志到localStorage:", e);
    }
  };

  /**
   * 控制台日志输出
   */
  const logError = (error) => {
    const logMethod = getLogMethod(error.level);
    logMethod(`[${error.type.toUpperCase()}] ${error.message}`, {
      id: error.id,
      level: error.level,
      context: error.context,
      stack: error.stack,
    });
  };

  /**
   * 向用户显示错误
   */
  const showErrorToUser = (error, customMessage) => {
    const message = customMessage || getUserFriendlyMessage(error);
    const color = getErrorColor(error.level);

    showSnackbar({
      message,
      color,
      timeout: getErrorTimeout(error.level),
      actions:
        error.level === ErrorLevels.CRITICAL
          ? [
              {
                text: "重新加载",
                action: () => window.location.reload(),
              },
            ]
          : undefined,
    });
  };

  /**
   * 上报错误到监控服务
   */
  const reportError = (error) => {
    // 这里可以集成第三方错误监控服务
    // 如 Sentry, LogRocket, Bugsnag 等

    if (process.env.NODE_ENV === "production") {
      // 示例：发送到错误监控API
      // fetch('/api/errors', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(error)
      // }).catch(() => {
      //   // 静默处理上报失败
      // })
    }
  };

  /**
   * 网络错误处理
   */
  const handleNetworkError = (error, options = {}) => {
    return handleError(error, {
      type: ErrorTypes.NETWORK,
      level: ErrorLevels.MEDIUM,
      ...options,
    });
  };

  /**
   * 验证错误处理
   */
  const handleValidationError = (error, options = {}) => {
    return handleError(error, {
      type: ErrorTypes.VALIDATION,
      level: ErrorLevels.LOW,
      ...options,
    });
  };

  /**
   * 系统错误处理
   */
  const handleSystemError = (error, options = {}) => {
    return handleError(error, {
      type: ErrorTypes.SYSTEM,
      level: ErrorLevels.HIGH,
      ...options,
    });
  };

  /**
   * 清理错误记录
   */
  const clearErrors = () => {
    errors.value = [];
    Object.keys(errorStats).forEach((key) => {
      errorStats[key] = 0;
    });
    localStorage.removeItem("errorLog");
  };

  /**
   * 获取错误统计
   */
  const getErrorStats = () => {
    return { ...errorStats };
  };

  // 工具函数
  const generateErrorId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  };

  const getLogMethod = (level) => {
    switch (level) {
      case ErrorLevels.LOW:
        return console.info;
      case ErrorLevels.MEDIUM:
        return console.warn;
      case ErrorLevels.HIGH:
        return console.error;
      case ErrorLevels.CRITICAL:
        return console.error;
      default:
        return console.log;
    }
  };

  const getUserFriendlyMessage = (error) => {
    switch (error.type) {
      case ErrorTypes.NETWORK:
        return "网络连接异常，请检查网络设置";
      case ErrorTypes.VALIDATION:
        return "输入数据格式不正确，请检查后重试";
      case ErrorTypes.SYSTEM:
        return "系统出现异常，请稍后重试";
      default:
        return "操作失败，请稍后重试";
    }
  };

  const getErrorColor = (level) => {
    switch (level) {
      case ErrorLevels.LOW:
        return "info";
      case ErrorLevels.MEDIUM:
        return "warning";
      case ErrorLevels.HIGH:
        return "error";
      case ErrorLevels.CRITICAL:
        return "error";
      default:
        return "error";
    }
  };

  const getErrorTimeout = (level) => {
    switch (level) {
      case ErrorLevels.LOW:
        return 3000;
      case ErrorLevels.MEDIUM:
        return 5000;
      case ErrorLevels.HIGH:
        return 8000;
      case ErrorLevels.CRITICAL:
        return 0; // 不自动关闭
      default:
        return 5000;
    }
  };

  return {
    // 状态
    errors,
    errorStats,

    // 常量
    ErrorTypes,
    ErrorLevels,

    // 方法
    handleError,
    handleNetworkError,
    handleValidationError,
    handleSystemError,
    clearErrors,
    getErrorStats,
  };
}

/**
 * 全局错误处理器
 */
export function setupGlobalErrorHandler() {
  const { handleError, ErrorTypes, ErrorLevels } = useErrorHandler();

  // 捕获未处理的Promise拒绝
  window.addEventListener("unhandledrejection", (event) => {
    handleError(event.reason, {
      type: ErrorTypes.SYSTEM,
      level: ErrorLevels.HIGH,
      context: { type: "unhandledrejection" },
    });
  });

  // 捕获JavaScript运行时错误
  window.addEventListener("error", (event) => {
    handleError(event.error || event.message, {
      type: ErrorTypes.SYSTEM,
      level: ErrorLevels.HIGH,
      context: {
        type: "javascript",
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      },
    });
  });

  // 捕获资源加载错误
  window.addEventListener(
    "error",
    (event) => {
      if (event.target !== window) {
        handleError(`资源加载失败: ${event.target.src || event.target.href}`, {
          type: ErrorTypes.NETWORK,
          level: ErrorLevels.MEDIUM,
          context: {
            type: "resource",
            tagName: event.target.tagName,
            src: event.target.src || event.target.href,
          },
        });
      }
    },
    true,
  );
}
