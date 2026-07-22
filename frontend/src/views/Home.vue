<template>
  <div class="home-page">
    <!-- Header -->
    <header class="header">
      <div class="header-inner" v-if="isLoggedIn">
        <div class="user-info">
          <span class="user-avatar">{{ userAvatar }}</span>
          <div>
            <div class="user-name">{{ userName }}</div>
            <div class="user-phone">{{ userPhone }}</div>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout">退出</button>
      </div>
      <div class="header-inner" v-else>
        <div class="brand">
          <span class="brand-icon">🛡️</span>
          <span class="brand-name">21天安全用网</span>
        </div>
        <button class="btn-login" @click="router.push('/login')">登录/注册</button>
      </div>
    </header>

    <!-- Hero / 标语 -->
    <section class="hero">
      <div class="hero-bg-decor">
        <span class="deco deco-1">⭐</span>
        <span class="deco deco-2">🌈</span>
        <span class="deco deco-3">✨</span>
        <span class="deco deco-4">🛡️</span>
        <span class="deco deco-5">💻</span>
      </div>
      <h1 class="hero-title">挑战21天</h1>
      <h2 class="hero-subtitle">安全上网小达人养成计划</h2>
      <p class="hero-desc">每天一个小任务，21天后你就是网络安全小专家！🔐</p>
    </section>

    <!-- 进度圆环 + 统计数据 (仅登录后显示) -->
    <section class="stats-section" v-if="isLoggedIn">
      <div class="progress-ring-container">
        <svg viewBox="0 0 200 200" class="progress-ring">
          <defs>
            <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="var(--color-accent)" />
              <stop offset="100%" stop-color="#e84393" />
            </linearGradient>
          </defs>
          <circle class="ring-bg" cx="100" cy="100" r="85" />
          <circle
            class="ring-fill"
            cx="100" cy="100" r="85"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="ringOffset"
          />
        </svg>
        <div class="ring-center">
          <span class="ring-num">{{ stats.total_days }}</span>
          <span class="ring-total">/21</span>
        </div>
      </div>

      <div class="stats-cards">
        <div class="stat-card">
          <span class="stat-icon">📅</span>
          <span class="stat-num">{{ stats.total_days }}</span>
          <span class="stat-label">累计打卡</span>
        </div>
        <div class="stat-card highlight">
          <span class="stat-icon">🔥</span>
          <span class="stat-num">{{ stats.streak_days }}</span>
          <span class="stat-label">连续打卡</span>
        </div>
        <div class="stat-card">
          <span class="stat-icon">🏆</span>
          <span class="stat-num">{{ 21 - stats.total_days }}</span>
          <span class="stat-label">剩余天数</span>
        </div>
      </div>
    </section>

    <!-- 登录前引导 -->
    <section class="guide-section" v-else>
      <div class="guide-card" @click="router.push('/login')">
        <span class="guide-icon">🚀</span>
        <div>
          <div class="guide-title">立即加入挑战</div>
          <div class="guide-desc">点击这里开始你的21天安全用网之旅！</div>
        </div>
        <span class="guide-arrow">→</span>
      </div>
    </section>

    <!-- 打卡日历 -->
    <section class="calendar-section">
      <div class="section-header">
        <h3 class="section-title">📅 打卡日历</h3>
        <button class="btn-link" @click="showCalendar = true">📅 日历详情</button>
      </div>
      <div class="day-grid">
        <div
          v-for="topic in topics"
          :key="topic.day"
          class="day-card"
          :class="{
            done: checkins[topic.day],
            today: !checkins[topic.day] && isToday(topic.day),
          }"
          @click="isLoggedIn ? onDayClick(topic.day) : router.push('/login')"
        >
          <span class="day-icon">{{ topic.icon }}</span>
          <span class="day-num">D{{ topic.day }}</span>
          <span v-if="checkins[topic.day]" class="day-check">✅</span>
          <span v-else-if="isToday(topic.day)" class="day-tag">今天</span>
        </div>
      </div>
    </section>

    <!-- 当日打卡任务 -->
    <section class="task-section" v-if="isLoggedIn">
      <div class="section-header">
        <h3 class="section-title">🎯 今日任务</h3>
        <span class="today-date">{{ todayDate }}</span>
      </div>

      <div class="task-list" v-if="todayTopic">
        <div
          class="task-card"
          :class="{ completed: checkins[todayTopic.day] }"
          @click="onDayClick(todayTopic.day)"
        >
          <div class="task-left">
            <span class="task-icon">{{ todayTopic.icon }}</span>
            <div>
              <div class="task-title">{{ todayTopic.title }}</div>
              <div class="task-desc">{{ todayTopic.question }}</div>
            </div>
          </div>
          <div class="task-status">
            <span v-if="checkins[todayTopic.day]" class="task-done">✅ 已完成</span>
            <span v-else class="task-go">去打卡 →</span>
          </div>
        </div>
      </div>

      <div class="task-list" v-else-if="stats.completed">
        <div class="all-done-banner">
          <span class="all-done-icon">🎉</span>
          <div>
            <div class="all-done-title">恭喜！全部完成！</div>
            <div class="all-done-desc">你已成功完成21天安全用网打卡挑战，太棒了！</div>
          </div>
        </div>
      </div>

      <div class="task-list" v-else>
        <div class="all-done-banner" style="background: #f0f4ff;">
          <span class="all-done-icon">☕</span>
          <div>
            <div class="all-done-title">今日任务已完成</div>
            <div class="all-done-desc">休息一下，明天继续加油哦～</div>
          </div>
        </div>
      </div>

      <!-- 下一关预告 -->
      <div v-if="nextTopic" class="next-preview">
        <span class="next-label">🔮 下一关预告</span>
        <span class="next-name">{{ nextTopic.title }}</span>
      </div>
    </section>

    <!-- 快捷入口 -->
    <section class="quick-links-section">
      <div class="quick-links-grid">
        <div class="quick-link" @click="router.push('/rules')">
          <span>📖</span><span>规则说明</span>
        </div>
        <div class="quick-link" @click="router.push('/notifications')">
          <span>🔔</span><span>消息通知</span>
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
        </div>
        <div class="quick-link" @click="router.push('/feedback')">
          <span>💬</span><span>反馈帮助</span>
        </div>
        <div class="quick-link" @click="router.push('/privacy')">
          <span>🔐</span><span>隐私设置</span>
        </div>
      </div>
    </section>

    <!-- 底部导航 -->
    <BottomNav activeTab="home" />
  </div>

  <!-- 日历弹窗 -->
  <div v-if="showCalendar" class="modal-overlay" @click.self="showCalendar = false">
    <div class="calendar-modal">
      <div class="modal-header">
        <h3>📅 打卡日历</h3>
        <button class="modal-close" @click="showCalendar = false">✕</button>
      </div>
      <div class="calendar-legend">
        <span><span class="legend-dot done"></span>已打卡</span>
        <span><span class="legend-dot today"></span>可打卡</span>
        <span><span class="legend-dot locked"></span>未解锁</span>
      </div>
      <div class="calendar-grid">
        <div v-for="topic in topics" :key="topic.day" class="cal-day"
          :class="{
            'cal-done': checkins[topic.day],
            'cal-today': !checkins[topic.day] && topic.day <= maxAvailableDay,
            'cal-locked': !checkins[topic.day] && topic.day > maxAvailableDay,
          }"
          @click="calDayClick(topic)"
        >
          <div class="cal-day-icon">{{ topic.icon }}</div>
          <div class="cal-day-num">{{ topic.day }}</div>
          <div class="cal-day-title">{{ topic.title }}</div>
          <div v-if="checkins[topic.day]" class="cal-mark">✅</div>
          <div v-else-if="topic.day > maxAvailableDay" class="cal-mark">🔒</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BottomNav from '../components/BottomNav.vue'
import { getTopics, getNotifications } from '../api/index'
import { fetchCheckIns, fetchStats, checkinMap, stats as storeStats } from '../stores/checkinStore'
import { user, isLoggedIn, logout as userLogout } from '../stores/userStore'

const router = useRouter()
const topics = ref([])
const checkins = checkinMap  // 共享缓存：{ [day]: record }
const stats = storeStats      // 共享缓存：{ total_days, streak_days, progress, completed }
const showRules = ref(false)
const showCalendar = ref(false)
const unreadCount = ref(0)

// 用户信息（来自 userStore）
const userName = computed(() => user.value?.nickname || '小朋友')
const userPhone = computed(() => user.value?.phone || '')
const userAvatar = computed(() => '🧒')

// 日期
const today = new Date()
const todayDate = `${today.getFullYear()}/${today.getMonth()+1}/${today.getDate()}`

// 进度圆环
const circumference = 2 * Math.PI * 85
const ringOffset = computed(() => {
  return circumference - (stats.progress / 100) * circumference
})

// 今日主题
const todayTopic = computed(() => {
  if (!topics.value.length) return null
  return topics.value.find(t => isToday(t.day))
})

// 下一关主题
const nextTopic = computed(() => {
  if (!topics.value.length) return null
  const maxDone = Math.max(0, ...Object.keys(checkins.value).map(Number))
  if (maxDone >= 21) return null
  return topics.value.find(t => t.day === maxDone + 1)
})

function isToday(day) {
  const doneDays = Object.keys(checkins.value).map(Number)
  const maxDone = doneDays.length ? Math.max(...doneDays) : 0
  if (doneDays.includes(day)) return false
  return day === maxDone + 1
}

function onDayClick(day) {
  if (!isLoggedIn.value) { router.push('/login'); return }
  router.push('/checkin?day=' + day)
}

function calDayClick(topic) {
  if (checkins.value[topic.day]) { router.push('/checkin'); return }
  if (topic.day > maxAvailableDay.value) return
  showCalendar.value = false
  router.push('/checkin')
}

async function loadData() {
  try {
    const [topicsRes] = await Promise.all([
      getTopics(),
      fetchCheckIns(),
      fetchStats(),
    ])
    topics.value = topicsRes.data
  } catch (e) {
    console.error(e)
  }
}

function handleLogout() {
  userLogout()
  router.go(0)
}

async function loadUnreadCount() {
  try {
    const res = await getNotifications()
    unreadCount.value = res.data.unread_count || 0
  } catch (e) {}
}

onMounted(() => {
  if (isLoggedIn.value) {
    loadData()
    loadUnreadCount()
  } else {
    // 未登录也加载主题数据
    getTopics().then(res => { topics.value = res.data }).catch(() => {})
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: var(--bg-gradient);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* Header */
.header {
  padding: 12px 16px;
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
}
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-avatar { font-size: 32px; }
.user-name { font-size: 15px; font-weight: 700; color: #333; }
.user-phone { font-size: 12px; color: #999; }
.btn-logout {
  background: #f5f5f5;
  border: none;
  padding: 6px 14px;
  border-radius: 15px;
  font-size: 13px;
  color: #666;
  cursor: pointer;
}
.brand { display: flex; align-items: center; gap: 8px; }
.brand-icon { font-size: 28px; }
.brand-name { font-size: 17px; font-weight: 800; color: #1a1a2e; }
.btn-login {
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

/* Hero */
.hero {
  text-align: center;
  padding: 30px 20px 20px;
  position: relative;
  overflow: hidden;
}
.hero-bg-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.deco {
  position: absolute;
  font-size: 24px;
  animation: float 3s ease-in-out infinite;
}
.deco-1 { top: 10%; left: 8%; animation-delay: 0s; }
.deco-2 { top: 20%; right: 10%; animation-delay: 0.5s; }
.deco-3 { bottom: 20%; left: 12%; animation-delay: 1s; }
.deco-4 { bottom: 10%; right: 8%; animation-delay: 1.5s; }
.deco-5 { top: 5%; left: 50%; animation-delay: 0.3s; }
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.hero-title {
  font-size: 32px;
  font-weight: 900;
  color: #0066CC;
  margin: 0;
  line-height: 1.2;
}
.hero-subtitle {
  font-size: 28px;
  font-weight: 900;
  color: #0066CC;
  margin: 0;
  line-height: 1.2;
}
.hero-desc {
  font-size: 14px;
  color: #888;
  margin: 0;
}

/* Progress Ring */
.stats-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 20px;
  margin-bottom: 20px;
}
.progress-ring-container {
  position: relative;
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}
.progress-ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.ring-bg {
  fill: none;
  stroke: #e8ecf4;
  stroke-width: 12;
}
.ring-fill {
  fill: none;
  stroke: url(#ringGrad);
  stroke-width: 12;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
}
.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.ring-num {
  font-size: 36px;
  font-weight: 900;
  color: var(--color-primary);
  line-height: 1;
}
.ring-total {
  font-size: 14px;
  color: #999;
  font-weight: 600;
}
.stats-cards {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.stat-card {
  background: white;
  border-radius: 14px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.stat-card.highlight {
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
}
.stat-icon { font-size: 24px; }
.stat-num { font-size: 22px; font-weight: 800; color: #333; }
.stat-label { font-size: 12px; color: #64748b; margin-left: auto; }

/* Guide section */
.guide-section {
  padding: 0 20px 20px;
}
.guide-card {
  background: var(--gradient-primary);
  border-radius: 20px;
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(59,130,246,0.35);
  transition: transform 0.2s;
}
.guide-card:active { transform: scale(0.98); }
.guide-icon { font-size: 40px; flex-shrink: 0; }
.guide-title { color: white; font-size: 18px; font-weight: 800; }
.guide-desc { color: rgba(255,255,255,0.8); font-size: 13px; margin-top: 4px; }
.guide-arrow { color: white; font-size: 22px; margin-left: auto; }

/* Calendar */
.calendar-section {
  padding: 0 16px;
  margin-bottom: 16px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.section-title {
  font-size: 17px;
  font-weight: 700;
  color: #333;
  margin: 0;
}
.btn-link {
  background: none;
  border: none;
  color: var(--color-accent);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.day-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}
.day-card {
  background: white;
  border-radius: 12px;
  padding: 10px 4px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  position: relative;
}
.day-card:active { transform: scale(0.95); }
.day-card.done {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}
.day-card.today {
  background: var(--gradient-primary);
  border: 2px solid var(--color-primary);
  animation: pulse 1.5s infinite;
}
.day-card.done .day-num, .day-card.today .day-num { color: white; }
.day-card.done .day-icon, .day-card.today .day-icon { filter: brightness(0) invert(1); }
.day-icon { font-size: 22px; display: block; margin-bottom: 2px; }
.day-num { font-size: 11px; color: #888; font-weight: 600; }
.day-check { font-size: 14px; position: absolute; top: 3px; right: 3px; color: white; }
.day-tag {
  position: absolute;
  top: 2px;
  right: 2px;
  background: var(--color-primary);
  color: white;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 8px;
}

/* Task Section */
.task-section {
  padding: 0 16px;
  margin-bottom: 16px;
}
.today-date {
  font-size: 12px;
  color: #999;
}
.task-card {
  background: white;
  border-radius: 20px;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: all 0.2s;
}
.task-card:active { transform: scale(0.98); }
.task-card.completed { background: #f0fff4; }
.task-left { display: flex; align-items: center; gap: 12px; flex: 1; }
.task-icon { font-size: 36px; flex-shrink: 0; }
.task-title { font-size: 16px; font-weight: 700; color: #333; }
.task-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.task-status { flex-shrink: 0; margin-left: 10px; }
.task-done { color: #22c55e; font-weight: 700; font-size: 14px; }
.task-go {
  background: var(--gradient-primary);
  color: white;
  padding: 6px 14px;
  border-radius: 15px;
  font-size: 13px;
  font-weight: 700;
}

.all-done-banner {
  background: #fffbe6;
  border-radius: 16px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.all-done-icon { font-size: 40px; flex-shrink: 0; }
.all-done-title { font-size: 16px; font-weight: 700; color: #333; }
.all-done-desc { font-size: 13px; color: #888; margin-top: 4px; }

.next-preview {
  margin-top: 12px;
  background: #f8f9fd;
  border-radius: 12px;
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.next-label { color: #888; font-weight: 600; }
.next-name { color: var(--color-accent); font-weight: 700; }

/* Rules */
.rules-section {
  padding: 0 16px;
  margin-bottom: 20px;
}
.rules-section .section-header {
  cursor: pointer;
}
.toggle-icon {
  font-size: 14px;
  color: #999;
}
.rules-content {
  background: white;
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.rule-item {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.rule-item:last-child { border-bottom: none; }
.rule-num {
  width: 26px;
  height: 26px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-dark));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}
.rule-title { font-size: 14px; font-weight: 700; color: #333; }
.rule-desc { font-size: 12px; color: #888; margin-top: 3px; line-height: 1.5; }

/* 快捷入口 */
.quick-links-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.quick-link {
  position: relative;
  background: white;
  border-radius: 14px;
  padding: 14px 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.15s;
}
.quick-link:active { transform: scale(0.95); }
.quick-link span:first-child { font-size: 28px; }
.quick-link span:last-of-type { font-size: 12px; color: #555; font-weight: 600; }
.badge {
  position: absolute; top: 6px; right: 8px;
  background: var(--color-danger); color: white;
  font-size: 10px; min-width: 16px; height: 16px;
  border-radius: 8px; display: flex;
  align-items: center; justify-content: center;
  padding: 0 4px; font-weight: 700;
}

/* 日历弹窗 */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  z-index: 999; display: flex; align-items: center;
  justify-content: center; animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.calendar-modal {
  background: white; border-radius: 20px;
  width: 90%; max-width: 500px; max-height: 80vh;
  overflow-y: auto; padding: 20px;
  animation: slideUp 0.3s;
}
@keyframes slideUp { from { transform: translateY(40px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.modal-header h3 { margin: 0; font-size: 18px; }
.modal-close { background: none; border: none; font-size: 22px; cursor: pointer; color: #999; }
.calendar-legend { display: flex; gap: 16px; margin-bottom: 14px; font-size: 12px; color: #777; }
.calendar-legend span { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.legend-dot.done { background: var(--color-success); }
.legend-dot.today { background: var(--color-accent); }
.legend-dot.locked { background: #ddd; }
.calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; }
.cal-day {
  border-radius: 10px; padding: 8px 4px;
  text-align: center; cursor: pointer;
  transition: transform 0.15s; position: relative;
}
.cal-day:active { transform: scale(0.95); }
.cal-done { background: #e8faf0; border: 2px solid var(--color-success); }
.cal-today { background: #eef0ff; border: 2px solid var(--color-accent); }
.cal-locked { background: #f5f5f5; border: 2px solid #eee; cursor: not-allowed; opacity: 0.6; }
.cal-day-icon { font-size: 20px; }
.cal-day-num { font-size: 11px; color: #888; font-weight: 700; }
.cal-day-title { font-size: 10px; color: #aaa; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cal-mark { position: absolute; top: 2px; right: 4px; font-size: 12px; }
</style>
