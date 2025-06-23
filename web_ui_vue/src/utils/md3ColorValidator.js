/**
 * Material Design 3 颜色验证工具
 * 验证颜色对比度是否符合WCAG 2.1 AA标准
 */

/**
 * 将十六进制颜色转换为RGB
 * @param {string} hex - 十六进制颜色值
 * @returns {Object} RGB颜色对象
 */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * 计算相对亮度
 * @param {Object} rgb - RGB颜色对象
 * @returns {number} 相对亮度值
 */
function getLuminance(rgb) {
  const { r, g, b } = rgb;

  const [rs, gs, bs] = [r, g, b].map((c) => {
    c = c / 255;
    return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  });

  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

/**
 * 计算对比度
 * @param {string} color1 - 第一个颜色（十六进制）
 * @param {string} color2 - 第二个颜色（十六进制）
 * @returns {number} 对比度值
 */
function getContrastRatio(color1, color2) {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  if (!rgb1 || !rgb2) return 0;

  const lum1 = getLuminance(rgb1);
  const lum2 = getLuminance(rgb2);

  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);

  return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * 验证颜色对比度是否符合WCAG标准
 * @param {string} foreground - 前景色
 * @param {string} background - 背景色
 * @param {string} level - 标准级别 ('AA' 或 'AAA')
 * @param {string} size - 文字大小 ('normal' 或 'large')
 * @returns {Object} 验证结果
 */
function validateContrast(
  foreground,
  background,
  level = "AA",
  size = "normal",
) {
  const ratio = getContrastRatio(foreground, background);

  const requirements = {
    AA: {
      normal: 4.5,
      large: 3.0,
    },
    AAA: {
      normal: 7.0,
      large: 4.5,
    },
  };

  const required = requirements[level][size];
  const passes = ratio >= required;

  return {
    ratio: Math.round(ratio * 100) / 100,
    required,
    passes,
    level,
    size,
  };
}

/**
 * MD3主题颜色定义
 */
const MD3_LIGHT_COLORS = {
  primary: "#1976D2",
  "primary-container": "#D3E3FD",
  "on-primary": "#FFFFFF",
  "on-primary-container": "#001C38",
  secondary: "#546E7A",
  "secondary-container": "#D7E3F7",
  "on-secondary": "#FFFFFF",
  "on-secondary-container": "#101C2B",
  tertiary: "#006064",
  "tertiary-container": "#B8EEFF",
  "on-tertiary": "#FFFFFF",
  "on-tertiary-container": "#001F24",
  error: "#BA1A1A",
  "error-container": "#FFDAD6",
  "on-error": "#FFFFFF",
  "on-error-container": "#410002",
  warning: "#D32F2F",
  "warning-container": "#FFDBCC",
  "on-warning": "#FFFFFF",
  "on-warning-container": "#2D1600",
  success: "#2E7D32",
  "success-container": "#C8E6C9",
  "on-success": "#FFFFFF",
  "on-success-container": "#0D2818",
  surface: "#FEFBFF",
  "surface-container-low": "#F7F2FA",
  "surface-container": "#F1ECF4",
  "surface-container-high": "#ECE6F0",
  "on-surface": "#1D1B20",
  "on-surface-variant": "#49454F",
  outline: "#79747E",
  background: "#FEFBFF",
  "on-background": "#1D1B20",
};

const MD3_DARK_COLORS = {
  primary: "#A8C8EC",
  "primary-container": "#004A77",
  "on-primary": "#003258",
  "on-primary-container": "#D3E3FD",
  secondary: "#BCC7DB",
  "secondary-container": "#3C4858",
  "on-secondary": "#263238",
  "on-secondary-container": "#D7E3F7",
  tertiary: "#86D2FF",
  "tertiary-container": "#004F5C",
  "on-tertiary": "#003640",
  "on-tertiary-container": "#B8EEFF",
  error: "#FFB4AB",
  "error-container": "#93000A",
  "on-error": "#690005",
  "on-error-container": "#FFDAD6",
  warning: "#FFB951",
  "warning-container": "#D32F2F",
  "on-warning": "#000000",
  "on-warning-container": "#FFFFFF",
  success: "#A6CF70",
  "success-container": "#1B5E20",
  "on-success": "#0D2818",
  "on-success-container": "#C8E6C9",
  surface: "#141218",
  "surface-container-low": "#1D1B20",
  "surface-container": "#211F26",
  "surface-container-high": "#2B2930",
  "on-surface": "#E6E0E9",
  "on-surface-variant": "#CAC4D0",
  outline: "#938F99",
  background: "#141218",
  "on-background": "#E6E0E9",
};

/**
 * 验证MD3主题颜色对比度
 * @param {boolean} isDark - 是否为深色主题
 * @returns {Object} 验证结果
 */
function validateMD3Theme(isDark = false) {
  const colors = isDark ? MD3_DARK_COLORS : MD3_LIGHT_COLORS;
  const results = {};

  // 验证主要颜色对比度
  const colorPairs = [
    ["primary", "on-primary"],
    ["primary-container", "on-primary-container"],
    ["secondary", "on-secondary"],
    ["secondary-container", "on-secondary-container"],
    ["tertiary", "on-tertiary"],
    ["tertiary-container", "on-tertiary-container"],
    ["error", "on-error"],
    ["error-container", "on-error-container"],
    ["warning", "on-warning"],
    ["warning-container", "on-warning-container"],
    ["success", "on-success"],
    ["success-container", "on-success-container"],
    ["surface", "on-surface"],
    ["surface-container-low", "on-surface"],
    ["surface-container", "on-surface"],
    ["surface-container-high", "on-surface"],
    ["background", "on-background"],
  ];

  colorPairs.forEach(([bg, fg]) => {
    if (colors[bg] && colors[fg]) {
      const key = `${bg}/${fg}`;
      results[key] = {
        normal: validateContrast(colors[fg], colors[bg], "AA", "normal"),
        large: validateContrast(colors[fg], colors[bg], "AA", "large"),
      };
    }
  });

  return results;
}

/**
 * 生成颜色验证报告
 * @returns {Object} 完整的验证报告
 */
function generateColorReport() {
  const lightResults = validateMD3Theme(false);
  const darkResults = validateMD3Theme(true);

  const report = {
    light: lightResults,
    dark: darkResults,
    summary: {
      light: {
        total: Object.keys(lightResults).length,
        passed: Object.values(lightResults).filter((r) => r.normal.passes)
          .length,
        failed: Object.values(lightResults).filter((r) => !r.normal.passes)
          .length,
      },
      dark: {
        total: Object.keys(darkResults).length,
        passed: Object.values(darkResults).filter((r) => r.normal.passes)
          .length,
        failed: Object.values(darkResults).filter((r) => !r.normal.passes)
          .length,
      },
    },
  };

  return report;
}

export {
  validateContrast,
  validateMD3Theme,
  generateColorReport,
  getContrastRatio,
  MD3_LIGHT_COLORS,
  MD3_DARK_COLORS,
};
