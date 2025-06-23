/**
 * 主题系统清理工具
 * 用于清理Monet相关的localStorage数据
 */

/**
 * 清理Monet相关的localStorage数据
 */
export function cleanupMonetThemeData() {
  const monetKeys = ["monet_seed_color", "monet_dark_mode", "monet_preset"];

  let cleanedCount = 0;

  monetKeys.forEach((key) => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key);
      cleanedCount++;
      console.log(`🧹 已清理localStorage键: ${key}`);
    }
  });

  if (cleanedCount > 0) {
    console.log(
      `✅ 清理完成，共清理了 ${cleanedCount} 个Monet相关的localStorage项`,
    );
  } else {
    console.log("ℹ️ 没有发现需要清理的Monet相关数据");
  }

  return cleanedCount;
}

/**
 * 重置主题为默认设置
 */
export function resetToDefaultTheme() {
  // 清理Monet数据
  cleanupMonetThemeData();

  // 设置默认主题
  localStorage.setItem("theme", "light");

  console.log("🎨 主题已重置为默认浅色主题");
}

/**
 * 检查是否存在Monet相关数据
 */
export function hasMonetThemeData() {
  const monetKeys = ["monet_seed_color", "monet_dark_mode", "monet_preset"];

  return monetKeys.some((key) => localStorage.getItem(key) !== null);
}

export default {
  cleanupMonetThemeData,
  resetToDefaultTheme,
  hasMonetThemeData,
};
