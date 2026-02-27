/**
 * 格式化数值，保留指定的小数位数
 * @param value 数值
 * @param decimals 小数位数，默认为2位
 * @returns 格式化后的字符串
 */
export function numberWithCommas(x: number | undefined, decimals: number = 0): string {
  if (x === undefined || x === null) {
    return '0';
  }
  
  // 使用 toFixed 保留指定位数的小数（并同时处理数值精度问题）
  // 然后移除不必要的后导0
  const fixedNum = Number(x.toFixed(decimals));
  
  // 格式化为带有千分位分隔符的字符串，同时保留小数部分
  return fixedNum.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

/**
 * 专门四舍五入到指定位数的函数
 * @param value 数值
 * @param decimals 小数位数
 * @returns 四舍五入后的数值
 */
export function roundToDecimal(value: number | undefined, decimals: number = 2): number {
  if (value === undefined || value === null) return 0;
  
  const factor = Math.pow(10, decimals);
  return Math.round(value * factor) / factor;
}