/**
 * 打卡数据共享缓存
 * Home、CheckIn、Stats 三个页面共用，避免重复请求。
 */
import { ref } from 'vue'
import { getCheckIns, getCheckInStats, getUsageStats } from '../api/index.js'

const CACHE_MAX_AGE = 60_000 // 缓存有效期 60 秒

// ── 打卡记录 ──
const checkins = ref([])          // 原始打卡记录数组
const checkinMap = ref({})        // { [day]: record } 快速查找
const checkinsLoaded = ref(false)
let checkinsLastFetch = 0
let checkinsPromise = null

// ── 打卡统计 ──
const stats = ref({})
const statsLoaded = ref(false)
let statsLastFetch = 0
let statsPromise = null

// ── 使用统计（Stats 页面专用） ──
const usageStats = ref({})
const usageStatsLoaded = ref(false)
let usageStatsLastFetch = 0
let usageStatsPromise = null

function isFresh(lastFetch) {
  return Date.now() - lastFetch < CACHE_MAX_AGE
}

/** 获取打卡记录（带缓存） */
export async function fetchCheckIns(force = false) {
  if (!force && checkinsLoaded.value && isFresh(checkinsLastFetch)) {
    return { checkins: checkins.value, checkinMap: checkinMap.value }
  }
  // 防止并发重复请求
  if (checkinsPromise) {
    await checkinsPromise
    return { checkins: checkins.value, checkinMap: checkinMap.value }
  }
  checkinsPromise = getCheckIns().then(res => {
    const data = res.data || []
    checkins.value = data
    const map = {}
    data.forEach(r => { map[r.day] = r })
    checkinMap.value = map
    checkinsLoaded.value = true
    checkinsLastFetch = Date.now()
    checkinsPromise = null
  }).catch(e => {
    checkinsPromise = null
    throw e
  })
  await checkinsPromise
  return { checkins: checkins.value, checkinMap: checkinMap.value }
}

/** 获取打卡统计（带缓存） */
export async function fetchStats(force = false) {
  if (!force && statsLoaded.value && isFresh(statsLastFetch)) {
    return stats.value
  }
  if (statsPromise) {
    await statsPromise
    return stats.value
  }
  statsPromise = getCheckInStats().then(res => {
    Object.assign(stats.value, res.data)
    statsLoaded.value = true
    statsLastFetch = Date.now()
    statsPromise = null
  }).catch(e => {
    statsPromise = null
    throw e
  })
  await statsPromise
  return stats.value
}

/** 获取使用统计（Stats 页面专用，带缓存） */
export async function fetchUsageStats(force = false) {
  if (!force && usageStatsLoaded.value && isFresh(usageStatsLastFetch)) {
    return usageStats.value
  }
  if (usageStatsPromise) {
    await usageStatsPromise
    return usageStats.value
  }
  usageStatsPromise = getUsageStats().then(res => {
    Object.assign(usageStats.value, res.data)
    usageStatsLoaded.value = true
    usageStatsLastFetch = Date.now()
    usageStatsPromise = null
  }).catch(e => {
    usageStatsPromise = null
    throw e
  })
  await usageStatsPromise
  return usageStats.value
}

/** 使缓存失效（打卡提交后调用） */
export function invalidateCheckins() {
  checkinsLoaded.value = false
  checkinsLastFetch = 0
  statsLoaded.value = false
  statsLastFetch = 0
  usageStatsLoaded.value = false
  usageStatsLastFetch = 0
}

export { checkins, checkinMap, stats, usageStats }
