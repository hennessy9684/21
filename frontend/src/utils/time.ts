/**
 * 相对时间格式化
 */
export function formatTime(dateStr: string | Date | null | undefined, fmt: 'full' | 'short' = 'full'): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (fmt === 'short') {
    return `${d.getMonth() + 1}月${d.getDate()}日`
  }
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${d.getMonth() + 1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
