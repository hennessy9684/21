<template>
  <div class="stats-page">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <span class="user-avatar">🧒</span>
        <div>
          <span class="user-name">{{ userName }}</span>
          <span class="user-sub">上网数据报告</span>
        </div>
      </div>
    </header>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-state">
      <span class="loading-icon">📊</span>
      <p>正在分析数据...</p>
    </div>

    <!-- 数据为空 -->
    <div v-else-if="!data.duration_trend?.length" class="empty-state">
      <span class="empty-icon">📭</span>
      <h3>暂无数据</h3>
      <p>完成打卡后这里会展示你的上网数据统计</p>
      <button class="btn-primary" @click="router.push('/checkin')">去打卡</button>
    </div>

    <div v-else>
      <!-- 周报卡片 -->
      <section class="report-section">
        <div class="report-card">
          <div class="report-header">
            <span class="report-icon">📋</span>
            <div>
              <h3>上网习惯周报</h3>
              <p>打卡 {{ data.report.total_days }} 天 · 健康评分</p>
            </div>
            <div class="score-ring">
              <span class="score-num" :class="scoreLevel">{{ data.report.score }}</span>
              <span class="score-label">分</span>
            </div>
          </div>
          <div class="report-stats">
            <div class="r-stat">
              <span class="r-num green">{{ data.healthy_days }}</span>
              <span class="r-label">健康上网天数</span>
            </div>
            <div class="r-stat">
              <span class="r-num red">{{ data.excessive_days }}</span>
              <span class="r-label">超标上网天数</span>
            </div>
            <div class="r-stat">
              <span class="r-num orange">{{ data.report.top_activity }}</span>
              <span class="r-label">最多上网活动</span>
            </div>
          </div>
          <div class="report-advice">
            <span class="advice-title">💡 改善建议</span>
            <ul>
              <li v-for="(tip, idx) in data.report.advice" :key="idx">{{ tip }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 上网时长分布 -->
      <section class="chart-section">
        <h3 class="chart-title">⏱️ 上网时长分布</h3>
        <div class="bar-chart">
          <div v-for="d in data.duration_distribution" :key="d.label" class="bar-item">
            <div class="bar-top">
              <span class="bar-value">{{ d.count }}天</span>
              <span class="bar-pct">{{ d.percent }}%</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ height: Math.max(d.percent, 4) + '%' }"
                :class="{ 'bar-short': d.label === '0-1小时', 'bar-mid': d.label === '1-3小时', 'bar-long': d.label === '3-5小时', 'bar-over': d.label === '5小时以上' }">
              </div>
            </div>
            <span class="bar-label">{{ d.label }}</span>
          </div>
        </div>
      </section>

      <!-- 上网用途占比 -->
      <section class="chart-section">
        <h3 class="chart-title">🎯 上网用途占比</h3>
        <div class="pie-area">
          <div class="pie-ring">
            <svg viewBox="0 0 200 200">
              <circle cx="100" cy="100" r="85" fill="none" stroke="#e8ecf4" stroke-width="20"/>
              <circle v-for="(act, idx) in pieArcs" :key="act.name" cx="100" cy="100" r="85"
                fill="none" :stroke="act.color" stroke-width="20"
                :stroke-dasharray="act.dash"
                :stroke-dashoffset="act.offset"
                transform="rotate(-90 100 100)"
                style="transition: all 0.8s ease;"
              />
            </svg>
            <div class="pie-center">
              <span class="pie-total">{{ data.activity_breakdown.length }}</span>
              <span class="pie-sub">类活动</span>
            </div>
          </div>

          <div class="legend">
            <div v-for="(act, idx) in data.activity_breakdown.slice(0, 6)" :key="act.name" class="legend-item">
              <span class="legend-dot" :style="{ background: colors[idx % colors.length] }"></span>
              <span class="legend-name">{{ act.name }}</span>
              <span class="legend-pct">{{ act.percent }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 每日时长趋势 -->
      <section class="chart-section">
        <h3 class="chart-title">📈 每日上网时长趋势</h3>
        <div class="trend-chart">
          <div v-for="(t, idx) in data.duration_trend" :key="t.day" class="trend-item">
            <div class="trend-bar-wrapper">
              <div class="trend-bar" 
                :style="{ height: (t.hours / 6 * 100) + '%' }"
                :class="{ 'trend-low': t.hours <= 0.5, 'trend-mid': t.hours <= 2, 'trend-high': t.hours > 2 }">
              </div>
            </div>
            <span class="trend-label">D{{ t.day }}</span>
          </div>
        </div>
      </section>

      <!-- 按周对比 -->
      <section class="chart-section">
        <h3 class="chart-title">📅 三周对比</h3>
        <div class="week-grid">
          <div v-for="w in data.weeks" :key="w.week" class="week-card"
            :class="{
              'week-good': w.excessive_rate <= 30,
              'week-warn': w.excessive_rate > 30 && w.excessive_rate <= 60,
              'week-bad': w.excessive_rate > 60,
            }">
            <span class="week-emoji">{{ w.excessive_rate <= 30 ? '✅' : w.excessive_rate <= 60 ? '⚠️' : '🔴' }}</span>
            <div class="week-label">{{ w.label }}</div>
            <div class="week-range">{{ w.range }}</div>
            <div class="week-stats">
              <span>打卡 {{ w.total_days }}天</span>
              <span :class="{ 'text-red': w.excessive_days > 0 }">超标 {{ w.excessive_days }}天</span>
            </div>
            <div class="week-rate" :class="{
              'text-green': w.excessive_rate <= 30,
              'text-orange': w.excessive_rate > 30 && w.excessive_rate <= 60,
              'text-red': w.excessive_rate > 60,
            }">
              超标率 {{ w.excessive_rate }}%
            </div>
          </div>
        </div>
      </section>

      <!-- 达标情况 -->
      <section class="chart-section">
        <h3 class="chart-title">🎯 健康达标情况</h3>
        <div class="health-card">
          <div class="health-ring-wrap">
            <svg viewBox="0 0 140 140" class="health-ring">
              <circle cx="70" cy="70" r="60" fill="none" stroke="#ffe0e0" stroke-width="14"/>
              <circle cx="70" cy="70" r="60" fill="none" stroke="#2ed573" stroke-width="14"
                :stroke-dasharray="377"
                :stroke-dashoffset="377 - 377 * data.report.healthy_rate / 100"
                stroke-linecap="round"
                transform="rotate(-90 70 70)"
              />
            </svg>
            <div class="health-center">
              <span class="health-pct">{{ data.report.healthy_rate }}%</span>
              <span class="health-sub">健康率</span>
            </div>
          </div>
          <div class="health-info">
            <div class="health-row">
              <span class="health-dot green"></span>
              <span>健康上网（0-3h）</span>
              <strong>{{ data.healthy_days }}天</strong>
            </div>
            <div class="health-row">
              <span class="health-dot red"></span>
              <span>超标上网（3h+）</span>
              <strong>{{ data.excessive_days }}天</strong>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 底部导航 -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="router.push('/')">
        <span>🏠</span><span>首页</span>
      </button>
      <button class="nav-item" @click="router.push('/checkin')">
        <span>📅</span><span>打卡</span>
      </button>
      <button class="nav-item active">
        <span>📊</span><span>统计</span>
      </button>
      <button class="nav-item" @click="router.push('/messages')">
        <span>💬</span><span>留言</span>
      </button>
      <button class="nav-item" @click="router.push('/my')">
        <span>👤</span><span>我的</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUsageStats } from '../api/index.js'

const router = useRouter()
const data = reactive({
  duration_distribution: [],
  duration_trend: [],
  activity_breakdown: [],
  excessive_days: 0,
  healthy_days: 0,
  excessive_rate: 0,
  weeks: [],
  report: {
    score: 0,
    healthy_rate: 0,
    top_activity: '',
    top_activity_percent: 0,
    most_common_duration: '',
    advice: [],
  },
})
const loading = ref(true)

const user = JSON.parse(localStorage.getItem('user') || '{}')
const userName = computed(() => user.nickname || '小朋友')

const colors = ['#3b82f6', '#ef4444', '#f59e0b', '#22c55e', '#8b5cf6', '#06b6d4', '#ec4899', '#6366f1']

const scoreLevel = computed(() => {
  const s = data.report.score
  if (s >= 80) return 'green'
  if (s >= 60) return 'orange'
  return 'red'
})

// 饼图弧线
const pieArcs = computed(() => {
  if (!data.activity_breakdown.length) return []
  let accumulated = 0
  return data.activity_breakdown.slice(0, 6).map((act, idx) => {
    const pct = act.percent / 100
    const dashLen = pct * 534  // circumference of r=85
    const offset = accumulated
    accumulated += dashLen
    return {
      name: act.name,
      color: colors[idx % colors.length],
      dash: `${dashLen} 534`,
      offset: -offset,
    }
  })
})

async function loadData() {
  try {
    const res = await getUsageStats()
    Object.assign(data, res.data)
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

onMounted(loadData)
</script>

<style scoped>
.stats-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #87CEEB 0%, #E0F4FF 40%, #F0FDF4 100%);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(12px);
}
.header-left { display: flex; align-items: center; gap: 8px; }
.user-avatar { font-size: 28px; }
.user-name { font-size: 16px; font-weight: 700; color: #333; }
.user-sub { font-size: 12px; color: #999; margin-left: 6px; }

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 40px;
  text-align: center;
}
.loading-icon, .empty-icon { font-size: 64px; margin-bottom: 16px; }
.loading-state p { color: #888; font-size: 15px; }
.empty-state h3 { color: #333; margin: 0 0 6px; }
.empty-state p { color: #888; font-size: 14px; margin: 0 0 20px; }
.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 20px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

/* Report */
.report-section { padding: 12px 16px; }
.report-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.report-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.report-icon { font-size: 36px; }
.report-header h3 { margin: 0; font-size: 17px; font-weight: 800; color: #333; }
.report-header p { margin: 2px 0 0; font-size: 12px; color: #888; }
.score-ring {
  margin-left: auto;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #f8f9fd;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.score-num { font-size: 22px; font-weight: 900; line-height: 1; }
.score-num.green { color: #2ed573; }
.score-num.orange { color: #ffa502; }
.score-num.red { color: #ff6b6b; }
.score-label { font-size: 11px; color: #888; }
.report-stats {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.r-stat {
  flex: 1;
  background: #f8f9fd;
  border-radius: 12px;
  padding: 10px;
  text-align: center;
}
.r-num { font-size: 18px; font-weight: 800; display: block; }
.r-num.green { color: #2ed573; }
.r-num.red { color: #ff6b6b; }
.r-num.orange { color: #ffa502; }
.r-label { font-size: 11px; color: #888; margin-top: 2px; display: block; }

.report-advice {
  background: #fffbeb;
  border-radius: 12px;
  padding: 14px;
}
.advice-title { font-size: 13px; font-weight: 700; color: #333; }
.report-advice ul {
  margin: 8px 0 0;
  padding-left: 18px;
}
.report-advice li {
  font-size: 12px;
  color: #666;
  line-height: 1.7;
}

/* Chart */
.chart-section {
  padding: 0 16px;
  margin-bottom: 20px;
}
.chart-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin: 0 0 14px;
}

/* Bar Chart */
.bar-chart {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex: 1;
}
.bar-top { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.bar-value { font-size: 13px; font-weight: 700; color: #333; }
.bar-pct { font-size: 11px; color: #888; }
.bar-track {
  width: 36px;
  height: 120px;
  background: #e8ecf4;
  border-radius: 10px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}
.bar-fill {
  width: 100%;
  border-radius: 10px 10px 0 0;
  transition: height 0.8s ease;
}
.bar-short { background: linear-gradient(180deg, #22c55e, #16a34a); }
.bar-mid { background: linear-gradient(180deg, #f59e0b, #d97706); }
.bar-long { background: linear-gradient(180deg, #f97316, #ea580c); }
.bar-over { background: linear-gradient(180deg, #dc2626, #b91c1c); }
.bar-label { font-size: 11px; color: #888; font-weight: 600; }

/* Pie */
.pie-area {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  gap: 20px;
}
.pie-ring {
  width: 130px;
  height: 130px;
  flex-shrink: 0;
  position: relative;
}
.pie-ring svg { width: 100%; height: 100%; }
.pie-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.pie-total { font-size: 28px; font-weight: 900; color: #333; line-height: 1; }
.pie-sub { font-size: 12px; color: #999; }
.legend { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-name { color: #555; flex: 1; }
.legend-pct { color: #888; font-weight: 600; }

/* Trend */
.trend-chart {
  background: white;
  border-radius: 16px;
  padding: 20px 12px;
  display: flex;
  justify-content: space-between;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  overflow-x: auto;
}
.trend-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 30px;
}
.trend-bar-wrapper {
  width: 14px;
  height: 100px;
  background: #e8ecf4;
  border-radius: 7px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}
.trend-bar {
  width: 100%;
  border-radius: 7px;
  transition: height 0.6s ease;
}
.trend-low { background: #2ed573; }
.trend-mid { background: #ffa502; }
.trend-high { background: #ff6b6b; }
.trend-label { font-size: 10px; color: #888; font-weight: 600; }

/* Week Grid */
.week-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.week-card {
  background: white;
  border-radius: 14px;
  padding: 16px 12px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.week-good { border-bottom: 3px solid #2ed573; }
.week-warn { border-bottom: 3px solid #ffa502; }
.week-bad { border-bottom: 3px solid #ff6b6b; }
.week-emoji { font-size: 28px; display: block; margin-bottom: 6px; }
.week-label { font-size: 14px; font-weight: 700; color: #333; }
.week-range { font-size: 11px; color: #999; margin: 2px 0 8px; }
.week-stats { font-size: 11px; color: #888; display: flex; flex-direction: column; gap: 2px; }
.week-rate { font-size: 14px; font-weight: 800; margin-top: 8px; }
.text-green { color: #2ed573; }
.text-orange { color: #ffa502; }
.text-red { color: #ff6b6b; }

/* Health */
.health-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  display: flex;
  align-items: center;
  gap: 24px;
}
.health-ring-wrap {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  position: relative;
}
.health-ring { width: 100%; height: 100%; }
.health-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.health-pct { font-size: 26px; font-weight: 900; color: #2ed573; line-height: 1; }
.health-sub { font-size: 11px; color: #888; }
.health-info { flex: 1; display: flex; flex-direction: column; gap: 14px; }
.health-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
}
.health-row strong { margin-left: auto; color: #333; }
.health-dot { width: 10px; height: 10px; border-radius: 50%; }
.health-dot.green { background: #2ed573; }
.health-dot.red { background: #ff6b6b; }

/* Bottom Nav */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  display: flex;
  justify-content: space-around;
  padding: 10px 0;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -2px 20px rgba(0,0,0,0.08);
  z-index: 50;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: none;
  border: none;
  font-size: 12px;
  color: #999;
  cursor: pointer;
  padding: 5px 16px;
}
.nav-item.active { color: #3b82f6; font-weight: 700; }
.nav-item span:first-child { font-size: 22px; }
</style>
