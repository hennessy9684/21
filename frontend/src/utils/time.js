/**
 * 相对时间格式化
 * @param {string|Date} dateStr - 日期字符串或 Date 对象
 * @param {'full'|'short'} [fmt='full'] - full 含时分, short 仅月日
 * @returns {string}
 */
export function formatTime(dateStr, fmt = 'full') {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (fmt === 'short') {
    return `${d.getMonth() + 1}月${d.getDate()}日`
  }
  const pad = n => n.toString().padStart(2, '0')
  return `${d.getMonth() + 1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
