<template>
  <div class="quiz-history-page">
    <header class="top-bar">
      <button class="btn-back" @click="router.back()">
        <span>←</span><span>返回</span>
      </button>
      <div class="top-title">答题历史</div>
      <div class="top-placeholder"></div>
    </header>

    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">📝</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total_quizzes }}</span>
          <span class="stat-label">累计答题</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.avg_score }}</span>
          <span class="stat-label">平均分</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.max_score }}</span>
          <span class="stat-label">最高分</span>
        </div>
      </div>
    </div>

    <div class="chart-section">
      <div class="section-header">
        <h2>📈 得分趋势</h2>
      </div>
      <div class="chart-card">
        <div v-if="trend.length > 0" class="chart-container">
          <svg viewBox="0 0 320 180" class="score-chart">
            <defs>
              <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:var(--color-accent);stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:var(--color-accent);stop-opacity:0" />
              </linearGradient>
            </defs>
            <g transform="translate(30, 10)">
              <line v-for="i in 5" :key="'h'+i" x1="0" :y1="(i-1)*40" x2="260" :y2="(i-1)*40" stroke="#e0e0e0" stroke-width="1" />
              <text v-for="i in 5" :key="'ht'+i" x="-8" :y="(i-1)*40+4" text-anchor="end" font-size="10" fill="#999">{{ (5-i)*25 }}</text>
              <line x1="0" y1="0" x2="0" y2="160" stroke="#e0e0e0" stroke-width="1" />
              <path :d="areaPath" fill="url(#scoreGradient)" />
              <path :d="linePath" fill="none" stroke="var(--color-accent)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
              <circle v-for="(point, idx) in chartPoints" :key="'p'+idx" :cx="point.x" :cy="point.y" r="6" fill="#fff" stroke="var(--color-accent)" stroke-width="2" />
              <text v-for="(point, idx) in chartPoints" :key="'pt'+idx" :x="point.x" :y="point.y-12" text-anchor="middle" font-size="11" font-weight="600" fill="var(--color-accent)">{{ point.score }}</text>
            </g>
            <g transform="translate(30, 170)">
              <text v-for="(t, idx) in trend" :key="'dt'+idx" :x="idx * (260 / (trend.length-1 || 1))" y="0" text-anchor="middle" font-size="10" fill="#999">D{{ t.day }}</text>
            </g>
          </svg>
        </div>
        <div v-else class="empty-chart">
          <span class="empty-icon">📊</span>
          <p>暂无答题记录</p>
        </div>
      </div>
    </div>

    <div class="history-section">
      <div class="section-header">
        <h2>📋 历史记录</h2>
      </div>
      <div class="history-list">
        <div v-for="item in history" :key="item.id" class="history-item" @click="toggleDetail(item.id)">
          <div class="history-left">
            <div class="day-badge">D{{ item.day }}</div>
            <div class="history-info">
              <span class="history-date">{{ formatDate(item.created_at) }}</span>
              <span class="history-count">{{ item.correct_count }}/{{ item.total_count }} 题</span>
            </div>
          </div>
          <div class="history-right">
            <div class="score-circle" :class="item.score >= 80 ? 'high' : (item.score >= 60 ? 'medium' : 'low')">
              {{ item.score }}
            </div>
            <span class="expand-icon">{{ expandedId === item.id ? '▲' : '▼' }}</span>
          </div>
          <div v-if="expandedId === item.id" class="history-detail">
            <div class="detail-title">答题详情</div>
            <div v-for="(answer, idx) in item.answers" :key="idx" class="answer-item" :class="{ correct: answer.is_correct, wrong: !answer.is_correct }">
              <span class="answer-icon">{{ answer.is_correct ? '✅' : '❌' }}</span>
              <span class="answer-text">第{{ idx + 1 }}题：你选 {{ answer.user_answer || '-' }}</span>
            </div>
          </div>
        </div>
        <div v-if="history.length === 0" class="empty-list">
          <span class="empty-icon">📝</span>
          <p>还没有答题记录，快去打卡答题吧！</p>
        </div>
      </div>
    </div>

    <BottomNav />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BottomNav from '../components/BottomNav.vue'
import { getQuizHistory } from '../api/index.js'

const router = useRouter()

const stats = reactive({ total_quizzes: 0, avg_score: 0, max_score: 0 })
const history = ref([])
const trend = ref([])
const expandedId = ref(null)

const chartPoints = computed(() => {
  if (trend.value.length === 0) return []
  const width = 260
  const height = 160
  const stepX = trend.value.length > 1 ? width / (trend.value.length - 1) : 0
  return trend.value.map((t, i) => ({
    x: i * stepX,
    y: height - (t.score / 100) * height,
    score: t.score,
  }))
})

const linePath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  return chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const areaPath = computed(() => {
  if (chartPoints.value.length === 0) return ''
  const height = 160
  const path = chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  const lastX = chartPoints.value[chartPoints.value.length - 1].x
  return `${path} L ${lastX} ${height} L 0 ${height} Z`
})

function formatDate(dateStr) {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

function toggleDetail(id) {
  expandedId.value = expandedId.value === id ? null : id
}

async function loadHistory() {
  try {
    const res = await getQuizHistory()
    const data = res.data
    stats.total_quizzes = data.total_quizzes || 0
    stats.avg_score = data.avg_score || 0
    stats.max_score = data.max_score || 0
    history.value = data.history || []
    trend.value = data.trend || []
  } catch (e) {
    console.error('加载答题历史失败:', e)
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.quiz-history-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8f4fd 0%, #fdf2f8 50%, #f0fdf4 100%);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 40;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #f5f5f5;
  border: none;
  padding: 6px 14px;
  border-radius: 15px;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  font-weight: 600;
}

.top-title {
  font-size: 17px;
  font-weight: 800;
  color: #333;
}

.top-placeholder {
  width: 60px;
}

.stats-section {
  display: flex;
  gap: 10px;
  padding: 16px;
}

.stat-card {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

.stat-icon {
  font-size: 28px;
  margin-bottom: 6px;
}

.stat-info {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 800;
  color: var(--color-accent);
}

.stat-label {
  font-size: 11px;
  color: #999;
}

.chart-section, .history-section {
  padding: 0 16px;
  margin-bottom: 20px;
}

.section-header {
  margin-bottom: 12px;
}

.section-header h2 {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin: 0;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.chart-container {
  display: flex;
  justify-content: center;
}

.score-chart {
  width: 100%;
  max-width: 360px;
  height: auto;
}

.empty-chart, .empty-list {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-chart p, .empty-list p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  background: white;
  border-radius: 16px;
  padding: 14px 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:active {
  transform: scale(0.98);
}

.history-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.day-badge {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-dark));
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 800;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-date {
  font-size: 13px;
  color: #333;
  font-weight: 600;
}

.history-count {
  font-size: 11px;
  color: #999;
}

.history-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  border: 3px solid;
}

.score-circle.high {
  background: #f0fff4;
  border-color: var(--color-success);
  color: var(--color-success);
}

.score-circle.medium {
  background: #fff9e6;
  border-color: #ffa502;
  color: #ffa502;
}

.score-circle.low {
  background: #fff5f5;
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.expand-icon {
  font-size: 12px;
  color: #999;
}

.history-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.detail-title {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.answer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.answer-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.answer-item.correct {
  color: var(--color-success);
}

.answer-item.wrong {
  color: #ff6b6b;
}
</style>