<template>
  <div class="checkin-page">
    <!-- 顶部返回栏 -->
    <header class="top-bar">
      <button class="btn-back" @click="goHome">
        <span>←</span><span>返回首页</span>
      </button>
      <div class="top-user">
        <span class="user-avatar">{{ userAvatar }}</span>
        <span class="user-name">{{ userName }}</span>
      </div>
    </header>

    <!-- 提交成功弹窗 -->
    <div v-if="submitted" class="success-overlay" @click.self="goHome">
      <div class="success-modal">
        <div class="confetti-container">
          <span v-for="i in 20" :key="i" class="confetti" :style="confettiStyle(i)"></span>
        </div>
        <div class="success-icon-wrap">
          <span class="success-emoji">🎉</span>
        </div>
        <h2>打卡成功！</h2>
        <div class="success-badge">第{{ successDay }}天</div>
        <p class="success-msg">
          进度 <strong>{{ successCount }}/21</strong>
        </p>
        <div class="progress-mini">
          <div class="progress-mini-fill" :style="{ width: successPercent + '%' }"></div>
        </div>
        <div class="success-detail">
          <div class="detail-row" v-if="lastSubmit.duration">
            <span>⏱️</span><span>{{ lastSubmit.duration }}</span>
          </div>
          <div class="detail-row" v-if="lastSubmit.activities">
            <span>🎮</span><span>{{ lastSubmit.activities }}</span>
          </div>
          <div class="detail-row" v-if="lastSubmit.mood">
            <span>😊</span><span>心情 {{ lastSubmit.mood }}</span>
          </div>
        </div>
        <p class="auto-back">{{ countdownText }}</p>
        <button class="btn-primary modal-btn" @click="goHome">返回首页</button>
      </div>
    </div>

    <!-- 查看已完成的打卡 -->
    <div v-else-if="viewingRecord" class="done-view">
      <div class="done-card">
        <div class="done-header">
          <span class="done-icon">{{ viewingRecord.icon }}</span>
          <div>
            <h3>第{{ viewingRecord.day }}天</h3>
            <h4>{{ viewingRecord.title }}</h4>
          </div>
        </div>
        <div class="done-body">
          <div class="done-field">
            <span class="done-label">📱 上网时长</span>
            <span class="done-value">{{ viewingRecord.online_duration || '-' }}</span>
          </div>
          <div class="done-field">
            <span class="done-label">🎮 上网活动</span>
            <span class="done-value">{{ viewingRecord.online_activities || '-' }}</span>
          </div>
          <div class="done-field">
            <span class="done-label">💡 上网影响</span>
            <span class="done-value">{{ viewingRecord.online_impact || '-' }}</span>
          </div>
          <div class="done-field">
            <span class="done-label">✍️ 你的回答</span>
            <span class="done-value">{{ viewingRecord.answer || '-' }}</span>
          </div>
          <div class="done-field">
            <span class="done-label">😊 心情</span>
            <span class="done-value">{{ viewingRecord.mood || '-' }}</span>
          </div>
        </div>
        <button class="btn-primary" @click="viewingRecord = null">关闭</button>
      </div>
    </div>

    <!-- 21天网格 + 问卷 -->
    <div v-else>
      <!-- 进度条 -->
      <div class="progress-section">
        <div class="progress-info">
          <span>打卡进度</span>
          <span class="progress-num">{{ stats.total_days }}/21</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: stats.progress + '%' }"></div>
        </div>
      </div>

      <!-- 21天网格 -->
      <div class="grid-section">
        <h2 class="section-title">📅 21天进度</h2>
        <div class="day-grid">
          <div
            v-for="topic in topics"
            :key="topic.day"
            class="day-card"
            :class="{
              done: checkins[topic.day],
              active: currentDay === topic.day && !checkins[topic.day],
              locked: topic.day > maxAvailableDay && !checkins[topic.day],
            }"
            @click="selectDay(topic)"
          >
            <span class="day-icon">{{ topic.icon }}</span>
            <span class="day-num">D{{ topic.day }}</span>
            <span v-if="checkins[topic.day]" class="day-check">✅</span>
            <span v-else-if="topic.day > maxAvailableDay" class="day-lock">🔒</span>
            <span v-else-if="currentDay === topic.day" class="day-tag">当前</span>
          </div>
        </div>
      </div>

      <!-- 当前日问卷表单（有可打卡的天即显示） -->
      <div class="form-section" v-if="currentTopic">
        <div class="form-card">
          <!-- 今日主题 -->
          <div class="topic-header">
            <span class="topic-icon">{{ currentTopic.icon }}</span>
            <div>
              <h3 class="topic-day">第{{ currentTopic.day }}天</h3>
              <h4 class="topic-title">{{ currentTopic.title }}</h4>
            </div>
          </div>
          <p class="topic-desc">{{ currentTopic.content }}</p>

          <!-- 问卷表单 -->
          <form @submit.prevent="handleSubmit">
            <!-- Q1: 上网时长 -->
            <div class="q-block">
              <div class="q-label">
                <span class="q-icon">⏱️</span>
                <span class="q-text">今日上网时长</span>
                <span class="q-required">*必填</span>
              </div>
              <div class="duration-options">
                <label
                  v-for="d in durations"
                  :key="d.value"
                  class="dur-option"
                  :class="{ selected: form.online_duration === d.value }"
                >
                  <input type="radio" v-model="form.online_duration" :value="d.value" hidden />
                  <span class="dur-emoji">{{ d.emoji }}</span>
                  <span class="dur-label">{{ d.label }}</span>
                </label>
              </div>
            </div>

            <!-- Q2: 上网活动 -->
            <div class="q-block">
              <div class="q-label">
                <span class="q-icon">🎮</span>
                <span class="q-text">今日主要上网活动</span>
                <span class="q-required">*多选</span>
              </div>
              <div class="activity-options">
                <label
                  v-for="a in activities"
                  :key="a.value"
                  class="act-option"
                  :class="{ selected: selectedActivities.includes(a.value) }"
                  @click="toggleActivity(a.value)"
                >
                  <span class="act-emoji">{{ a.emoji }}</span>
                  <span class="act-label">{{ a.label }}</span>
                  <span v-if="selectedActivities.includes(a.value)" class="act-check">✓</span>
                </label>
              </div>
            </div>

            <!-- Q3: 上网带来的影响 -->
            <div class="q-block">
              <div class="q-label">
                <span class="q-icon">💡</span>
                <span class="q-text">今日上网带来的影响</span>
                <span class="q-required">*必填</span>
              </div>
              <textarea
                v-model="form.online_impact"
                class="q-textarea"
                placeholder="说说今天上网给你带来了什么影响？好的和不好的都可以写..."
                rows="3"
              ></textarea>
            </div>

            <!-- Q4: 今日打卡问题 -->
            <div class="q-block">
              <div class="q-label">
                <span class="q-icon">✍️</span>
                <span class="q-text">今日思考题</span>
              </div>
              <div class="topic-question-box">
                <p>{{ currentTopic.question }}</p>
              </div>
              <textarea
                v-model="form.answer"
                class="q-textarea"
                placeholder="写下你的想法吧...（至少5个字）"
                rows="3"
              ></textarea>
            </div>

            <!-- 心情 -->
            <div class="q-block">
              <div class="q-label">
                <span class="q-icon">😊</span>
                <span class="q-text">今天的心情</span>
              </div>
              <div class="mood-selector">
                <span
                  v-for="m in moods"
                  :key="m"
                  class="mood-option"
                  :class="{ selected: form.mood === m }"
                  @click="form.mood = m"
                >{{ m }}</span>
              </div>
            </div>

            <!-- 错误提示 -->
            <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

            <!-- 答题测评 -->
            <div class="quiz-section">
              <div class="quiz-header">
                <span>🧠 安全知识测评（必答）</span>
                <span class="quiz-status">{{ quizResult ? '✅ 已完成' : quizAllAnswered() ? '📝 待提交' : '⚠️ 未完成' }}</span>
              </div>

              <div v-if="quizResult" class="quiz-result-card">
                <div class="quiz-score-circle" :class="quizResult.score >= 80 ? 'pass' : 'fail'">
                  <span class="quiz-score-num">{{ quizResult.score }}</span>
                  <span class="quiz-score-label">得分</span>
                </div>
                <div class="quiz-result-detail">
                  <p class="quiz-result-text">
                    {{ quizResult.correct }}/{{ quizResult.total }} 题正确
                    {{ quizResult.score >= 80 ? ' 🎉 太棒了！' : ' 💪 继续加油！' }}
                  </p>
                  <button type="button" class="quiz-retry-btn" @click="quizRetry">重新答题</button>
                </div>
                <div class="quiz-explanations" v-if="quizResult.results">
                  <div v-for="(r, i) in quizResult.results" :key="i" class="quiz-explain-item" :class="{ correct: r.is_correct, wrong: !r.is_correct }">
                    <span class="quiz-explain-icon">{{ r.is_correct ? '✅' : '❌' }}</span>
                    <div class="quiz-explain-text">
                      <p>{{ r.question || ('题目 #' + r.id) }}</p>
                      <p>
                        正确答案：
                         <span v-if="r.q_type === 'true_false'">{{ r.correct_answer === 'A' ? '✅ 正确' : '❌ 错误' }}</span>
                        <span v-else>{{ r.correct_answer }}</span>
                        （你选：
                         <span v-if="r.q_type === 'true_false'">{{ r.user_answer === 'A' ? '✅ 正确' : r.user_answer === 'B' ? '❌ 错误' : (r.user_answer || '-') }}</span>
                        <span v-else>{{ r.user_answer || '-' }}</span>
                        ）
                      </p>
                      <p class="quiz-explain-detail" v-if="r.explanation">{{ r.explanation }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="quiz-body">
                <p class="quiz-tip">请回答以下安全问题（共 {{ quizQuestions.length }} 题，全部答完才能提交打卡）</p>
                <div v-for="(q, qi) in quizQuestions" :key="q.id" class="quiz-item">
                  <p class="quiz-q-title">
                    {{ qi + 1 }}. {{ q.question }}
                    <span v-if="q.q_type === 'true_false'" class="quiz-tf-badge">判断题</span>
                  </p>
                  <div class="quiz-options">
                    <label
                      v-for="(text, key) in filteredOptions(q)"
                      :key="key"
                      class="quiz-option"
                      :class="{ selected: quizAnswerMap[q.id] === key }"
                      @click="selectQuizAnswer(q.id, key)"
                    >
                      <span class="quiz-radio-dot" :class="{ checked: quizAnswerMap[q.id] === key }"></span>
                      <span>
                        <template v-if="q.q_type === 'true_false'">
                           {{ key === 'A' ? '✅ 正确' : '❌ 错误' }}
                        </template>
                        <template v-else>
                          {{ key }}. {{ text }}
                        </template>
                      </span>
                    </label>
                  </div>
                </div>
                <button type="button" class="quiz-submit-btn" @click="handleQuizSubmit" :disabled="quizSubmitted || !quizAllAnswered()">
                  {{ quizSubmitted ? '提交中...' : '✅ 提交答案' }}
                </button>
              </div>
            </div>

            <!-- 提交按钮 -->
            <button type="submit" class="btn-submit" :disabled="submitting">
              {{ submitting ? '⏳ 提交中...' : '✅ 完成打卡，提交问卷' }}
            </button>
          </form>
        </div>
      </div>

      <!-- 全部完成 -->
      <div class="form-section" v-else-if="stats.completed">
        <div class="all-done-card">
          <span class="all-done-icon">🏆</span>
          <h3>恭喜！21天全部完成！</h3>
          <p>你已经是网络安全小达人了！</p>
          <button class="btn-primary" @click="goHome">返回首页</button>
        </div>
      </div>

      <!-- 暂无任务 -->
      <div class="form-section" v-else>
        <div class="all-done-card" style="background: #f0f4ff;">
          <span class="all-done-icon">☕</span>
          <h3>暂无打卡任务</h3>
          <p>休息一下，明天继续加油～</p>
          <button class="btn-primary" @click="goHome">返回首页</button>
        </div>
      </div>
    </div>
    <!-- 底部导航 -->
    <nav class="bottom-nav">
      <button class="nav-item" @click="router.push('/')">
        <span>🏠</span><span>首页</span>
      </button>
      <button class="nav-item active">
        <span>📅</span><span>打卡</span>
      </button>
      <button class="nav-item" @click="router.push('/stats')">
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
import { useRouter, useRoute } from 'vue-router'
import { getTopics, getCheckIns, submitCheckIn, getCheckInStats, getQuizQuestions, submitQuiz as submitQuizApi } from '../api/index.js'

const router = useRouter()
const route = useRoute()

const topics = ref([])
const checkins = reactive({})
const stats = reactive({ total_days: 0, streak_days: 0, progress: 0, completed: false })
const currentDay = ref(0)
const submitting = ref(false)
const errorMsg = ref('')
const submitted = ref(false)
const successDay = ref(0)
const successCount = ref(0)
const successPercent = ref(0)
const countdownText = ref('即将返回首页...')
const lastSubmit = reactive({ duration: '', activities: '', mood: '' })
const viewingRecord = ref(null)
const selectedActivities = ref([])

// 表单
const form = reactive({
  online_duration: '',
  online_activities: '',
  online_impact: '',
  answer: '',
  mood: '😊',
})

// 答题测评
const quizQuestions = ref([])
const quizAnswerMap = ref({})
const quizSubmitted = ref(false)
const quizResult = ref(null)

function selectQuizAnswer(qid, option) {
  quizAnswerMap.value = { ...quizAnswerMap.value, [qid]: option }
}

function quizAllAnswered() {
  return quizQuestions.value.every(q => quizAnswerMap.value[q.id])
}

function filteredOptions(q) {
  const opts = q.options || {}
  if (q.q_type === 'true_false') {
    return { A: opts.A || '正确', B: opts.B || '错误' }
  }
  // Filter out empty options for choice questions
  const filtered = {}
  for (const [k, v] of Object.entries(opts)) {
    if (v) filtered[k] = v
  }
  return filtered
}

async function loadQuiz() {
  try {
    const day = currentDay.value || (stats.total_days + 1)
    const res = await getQuizQuestions(day)
    quizQuestions.value = res.data.questions || []
    const init = {}
    quizQuestions.value.forEach(q => { init[q.id] = '' })
    quizAnswerMap.value = init
    quizResult.value = null
    quizSubmitted.value = false
    if (quizQuestions.value.length === 0) {
      loadDefaultQuiz(day)
    }
  } catch (e) {
    console.error('加载题目失败:', e)
    loadDefaultQuiz(currentDay.value || (stats.total_days + 1))
  }
}

function loadDefaultQuiz(day) {
  const defaultQuizzes = [
    { id: 1001, question: '以下哪个密码最安全？', options: { A: '123456', B: 'password', C: 'W@b#5e$8q', D: 'abcdef' } },
    { id: 1002, question: '收到陌生人发来的链接应该怎么做？', options: { A: '直接点击', B: '先确认来源安全', C: '转发给朋友', D: '保存下来' } },
    { id: 1003, question: '在公共WiFi环境下，以下哪种做法最安全？', options: { A: '网上购物', B: '登录银行账户', C: '只浏览新闻', D: '发送密码' } },
    { id: 1004, question: '网络诈骗通常会用什么方式引诱你？', options: { A: '告诉你中大奖', B: '要求转账', C: '冒充客服', D: '以上都是' } },
    { id: 1005, question: '个人隐私信息包括哪些？', options: { A: '手机号', B: '身份证号', C: '家庭住址', D: '以上都是' } },
    { id: 1006, question: '遇到网络暴力应该怎么做？', options: { A: '互骂回去', B: '沉默忍受', C: '保留证据并举报', D: '告诉所有人' } },
    { id: 1007, question: '密码应该多长时间更换一次？', options: { A: '从不更换', B: '半年一次', C: '一年一次', D: '三个月一次' } },
    { id: 1008, question: '钓鱼网站的特征是什么？', options: { A: '网址很像正规网站', B: '要求输入账号密码', C: '页面粗糙', D: '以上都是' } },
    { id: 1009, question: '游戏中陌生人要你充值应该怎么做？', options: { A: '立即充值', B: '拒绝并举报', C: '先充一点试试', D: '借给他钱' } },
    { id: 1010, question: '刷短视频遇到不良内容应该？', options: { A: '继续看', B: '举报并屏蔽', C: '分享给别人', D: '下载保存' } },
  ]
  const startIdx = (day - 1) % 6
  quizQuestions.value = defaultQuizzes.slice(startIdx, startIdx + 5)
  const init = {}
  quizQuestions.value.forEach(q => { init[q.id] = '' })
  quizAnswerMap.value = init
  quizResult.value = null
  quizSubmitted.value = false
}

async function handleQuizSubmit() {
  if (!quizAllAnswered()) {
    errorMsg.value = '请完成所有题目再提交'
    return
  }
  const answers = quizQuestions.value.map(q => ({ id: q.id, answer: quizAnswerMap.value[q.id] }))
  const day = currentDay.value || (stats.total_days + 1)
  try {
    quizSubmitted.value = true
    const res = await submitQuizApi(answers, day)
    quizResult.value = res.data
  } catch (e) {
    console.error('提交答题失败:', e)
    errorMsg.value = '答题提交失败，请重试'
    quizSubmitted.value = false
  }
}

function quizRetry() {
  const init = {}
  quizQuestions.value.forEach(q => { init[q.id] = '' })
  quizAnswerMap.value = init
  quizResult.value = null
  quizSubmitted.value = false
}

// 上网时长选项
const durations = [
  { value: '0-1小时', label: '0-1小时', emoji: '📱' },
  { value: '1-3小时', label: '1-3小时', emoji: '🕐' },
  { value: '3-5小时', label: '3-5小时', emoji: '🕒' },
  { value: '5小时以上', label: '5小时以上', emoji: '🕔' },
]

// 上网活动选项
const activities = [
  { value: '学习查资料', label: '学习查资料', emoji: '📚' },
  { value: '玩游戏', label: '玩游戏', emoji: '🎮' },
  { value: '刷短视频', label: '刷短视频', emoji: '🎬' },
  { value: '社交聊天', label: '社交聊天', emoji: '💬' },
  { value: '看视频追剧', label: '看视频追剧', emoji: '📺' },
  { value: '听音乐', label: '听音乐', emoji: '🎵' },
  { value: '网购', label: '网购', emoji: '🛒' },
  { value: '其他', label: '其他', emoji: '📌' },
]

const moods = ['😊', '😄', '🥰', '🤩', '😎', '🤗', '💪', '🔥', '😅', '🤔']

const user = JSON.parse(localStorage.getItem('user') || '{}')
const userName = computed(() => user.nickname || '小朋友')
const userAvatar = computed(() => '🧒')

// 当前可打卡天数
const maxAvailableDay = computed(() => {
  const maxChecked = Math.max(0, ...Object.keys(checkins).map(Number))
  return Math.min(maxChecked + 1, 21)
})

// 当前打卡主题
const currentTopic = computed(() => {
  const targetDay = currentDay.value || maxAvailableDay.value
  if (!targetDay || targetDay > 21) return null
  if (checkins[targetDay]) return null
  return topics.value.find(t => t.day === targetDay)
})

// 切换活动选择
function toggleActivity(val) {
  const idx = selectedActivities.value.indexOf(val)
  if (idx >= 0) {
    selectedActivities.value.splice(idx, 1)
  } else {
    selectedActivities.value.push(val)
  }
  form.online_activities = selectedActivities.value.join('、')
}

// 选择某天
async function selectDay(topic) {
  if (checkins[topic.day]) {
    // 查看已完成的记录
    viewingRecord.value = {
      ...checkins[topic.day],
      icon: topic.icon,
      title: topic.title,
    }
    return
  }
  if (topic.day > maxAvailableDay.value) return
  viewingRecord.value = null
  currentDay.value = topic.day
  resetForm()
  await loadQuiz()
  window.scrollTo({ top: document.querySelector('.form-section')?.offsetTop - 20, behavior: 'smooth' })
}

function resetForm() {
  form.online_duration = ''
  form.online_activities = ''
  form.online_impact = ''
  form.answer = ''
  form.mood = '😊'
  selectedActivities.value = []
  errorMsg.value = ''
}

function goHome() {
  router.push('/')
}

function confettiStyle(i) {
  const colors = ['#ff6b6b','#ffa502','#2ed573','#1e90ff','#a55eea','#ff6348','#7bed9f','#ffc048']
  return {
    left: Math.random() * 100 + '%',
    background: colors[i % colors.length],
    animationDelay: Math.random() * 1.5 + 's',
    animationDuration: (2 + Math.random() * 2) + 's',
    width: (6 + Math.random() * 6) + 'px',
    height: (6 + Math.random() * 8) + 'px',
  }
}

async function loadData() {
  try {
    const [topicsRes, checkinRes, statsRes] = await Promise.all([
      getTopics(),
      getCheckIns(),
      getCheckInStats(),
    ])
    topics.value = topicsRes.data
    checkinRes.data.forEach(r => { checkins[r.day] = r })
    Object.assign(stats, statsRes.data)
  } catch (e) {
    console.error(e)
  }
}

async function handleSubmit() {
  errorMsg.value = ''

  // 前端校验
  if (!form.online_duration) {
    errorMsg.value = '请选择今日上网时长'
    return
  }
  if (selectedActivities.value.length === 0) {
    errorMsg.value = '请至少选择一项上网活动'
    return
  }
  if (!form.online_impact.trim()) {
    errorMsg.value = '请填写上网带来的影响'
    return
  }
  if (!form.answer.trim() || form.answer.trim().length < 5) {
    errorMsg.value = '请认真回答思考题（至少5个字）'
    return
  }

  // 答题测评必答
  if (!quizResult.value) {
    if (!quizAllAnswered()) {
      errorMsg.value = '请先完成安全知识测评（全部题目）'
      return
    }
    errorMsg.value = '请先提交安全知识测评答案'
    return
  }

  const day = currentTopic.value.day
  submitting.value = true

  try {
    const res = await submitCheckIn({
      day: currentTopic.value.day,
      answer: form.answer.trim(),
      online_duration: form.online_duration,
      online_activities: form.online_activities,
      online_impact: form.online_impact.trim(),
      mood: form.mood,
    })
    const data = res.data

    // 更新本地数据
    checkins[day] = data.record
    stats.total_days++
    stats.progress = Math.round(stats.total_days / 21 * 100)
    if (stats.total_days > stats.streak_days) stats.streak_days = stats.total_days

    // 显示成功画面
    lastSubmit.duration = form.online_duration
    lastSubmit.activities = form.online_activities
    lastSubmit.mood = form.mood
    successDay.value = day
    successCount.value = stats.total_days
    successPercent.value = stats.progress
    submitted.value = true

    // 倒计时返回
    let sec = 3
    countdownText.value = `${sec}秒后自动返回首页...`
    const timer = setInterval(() => {
      sec--
      if (sec <= 0) {
        clearInterval(timer)
        router.push('/')
      } else {
        countdownText.value = `${sec}秒后自动返回首页...`
      }
    }, 1000)

  } catch (e) {
    const errData = e.response?.data
    errorMsg.value = errData?.error || '提交失败，请稍后重试'
  }
  submitting.value = false
}

onMounted(async () => {
  await loadData()
  loadQuiz()
})
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8f4fd 0%, #fdf2f8 50%, #f0fdf4 100%);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* Top Bar */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(12px);
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
.top-user { display: flex; align-items: center; gap: 8px; }
.user-avatar { font-size: 28px; }
.user-name { font-size: 15px; font-weight: 700; color: #333; }

/* Progress */
.progress-section {
  padding: 0 16px 16px;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #888;
  margin-bottom: 6px;
}
.progress-num { font-weight: 700; color: #667eea; }
.progress-bar {
  height: 8px;
  background: #e8ecf4;
  border-radius: 8px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #e84393);
  border-radius: 8px;
  transition: width 0.5s;
}

/* Grid */
.grid-section {
  padding: 0 16px;
  margin-bottom: 20px;
}
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  margin: 0 0 12px;
}
.day-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}
.day-card {
  background: white;
  border-radius: 10px;
  padding: 8px 2px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04);
  position: relative;
  font-size: 11px;
}
.day-card:active { transform: scale(0.95); }
.day-card.done {
  background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
}
.day-card.active {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border: 2px solid #667eea;
}
.day-card.locked { opacity: 0.45; cursor: not-allowed; }
.day-icon { font-size: 18px; display: block; }
.day-num { font-size: 10px; color: #999; font-weight: 600; }
.day-check, .day-lock { font-size: 10px; position: absolute; top: 2px; right: 2px; }
.day-tag {
  position: absolute;
  top: 1px; right: 1px;
  background: #667eea;
  color: white;
  font-size: 9px;
  padding: 1px 4px;
  border-radius: 5px;
}

/* Form Section */
.form-section { padding: 0 16px; }
.form-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.topic-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.topic-icon { font-size: 40px; }
.topic-day { font-size: 13px; color: #667eea; margin: 0; }
.topic-title { font-size: 18px; color: #333; margin: 2px 0 0; font-weight: 800; }
.topic-desc { font-size: 13px; color: #888; margin: 0 0 18px; line-height: 1.5; }
.topic-question-box {
  background: #f0f4ff;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #555;
  line-height: 1.5;
}
.topic-question-box p { margin: 0; }

/* Question Blocks */
.q-block {
  margin-bottom: 20px;
}
.q-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}
.q-icon { font-size: 16px; }
.q-text { font-size: 14px; font-weight: 700; color: #333; }
.q-required {
  font-size: 11px;
  color: #fff;
  background: #ff6b6b;
  padding: 1px 6px;
  border-radius: 8px;
}

/* Duration */
.duration-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.dur-option {
  background: #f5f7fb;
  border-radius: 12px;
  padding: 12px 8px;
  text-align: center;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.dur-option.selected {
  border-color: #667eea;
  background: #f0f4ff;
}
.dur-emoji { font-size: 24px; }
.dur-label { font-size: 13px; font-weight: 600; color: #555; }
.dur-option.selected .dur-label { color: #667eea; }

/* Activities */
.activity-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}
.act-option {
  background: #f5f7fb;
  border-radius: 10px;
  padding: 10px 8px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  position: relative;
}
.act-option.selected {
  border-color: #667eea;
  background: #f0f4ff;
}
.act-emoji { font-size: 18px; }
.act-label { font-size: 12px; font-weight: 600; color: #555; }
.act-option.selected .act-label { color: #667eea; }
.act-check {
  position: absolute;
  right: 6px;
  top: 6px;
  width: 18px;
  height: 18px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.q-textarea {
  width: 100%;
  border: 2px solid #e8ecf4;
  border-radius: 12px;
  padding: 12px;
  font-size: 14px;
  resize: none;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color 0.2s;
}
.q-textarea:focus { border-color: #667eea; }

/* Mood */
.mood-selector {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.mood-option {
  font-size: 28px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 10px;
  transition: all 0.2s;
  opacity: 0.4;
}
.mood-option.selected, .mood-option:hover {
  opacity: 1;
  transform: scale(1.15);
  background: #f0f4ff;
}

.error-text {
  color: #ff4757;
  font-size: 13px;
  text-align: center;
  margin: 0 0 10px;
}

.btn-submit {
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 15px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-submit:hover:not(:disabled) { transform: translateY(-2px); }
.btn-submit:disabled { opacity: 0.6; transform: none; }

.btn-primary {
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 15px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 16px;
}

/* Success Modal */
.success-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 999; padding: 20px;
  animation: fadeIn 0.3s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.success-modal {
  background: white; border-radius: 28px; padding: 36px 28px 28px;
  width: 100%; max-width: 360px; text-align: center;
  position: relative; overflow: hidden;
  box-shadow: 0 24px 60px rgba(0,0,0,0.3);
  animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
@keyframes popIn {
  from { transform: scale(0.6); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
.success-icon-wrap {
  width: 80px; height: 80px; margin: 0 auto 10px;
  background: linear-gradient(135deg, #2ed573, #7bed9f);
  border-radius: 50%; display: flex;
  align-items: center; justify-content: center;
  animation: pulse 0.6s infinite alternate;
}
@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.08); }
}
.success-emoji { font-size: 40px; }
.success-modal h2 {
  color: #2ed573; margin: 0 0 8px; font-size: 24px; font-weight: 800;
}
.success-badge {
  display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; font-size: 13px; padding: 4px 16px;
  border-radius: 20px; font-weight: 700; margin-bottom: 8px;
}
.success-msg { color: #666; font-size: 14px; margin: 0 0 16px; }
.progress-mini {
  height: 8px;
  background: #e8ecf4;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}
.progress-mini-fill {
  height: 100%;
  background: linear-gradient(90deg, #2ed573, #7bed9f);
  border-radius: 8px;
  transition: width 0.8s ease;
}
.success-detail {
  margin: 12px 0;
  background: #f8faf9;
  border-radius: 12px;
  padding: 10px 14px;
}
.detail-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 12px; color: #666; padding: 3px 0;
}
.detail-row span:first-child { font-size: 14px; }
.auto-back { color: #aaa; font-size: 13px; margin: 10px 0 4px; }
.modal-btn { margin-top: 8px; }

/* Confetti */
.confetti-container {
  position: absolute; top: 0; left: 0; right: 0; height: 100%;
  pointer-events: none; overflow: hidden; z-index: 0;
}
.confetti {
  position: absolute; top: -10px; border-radius: 2px;
  animation: confettiFall linear forwards;
}
@keyframes confettiFall {
  0% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(500px) rotate(720deg); opacity: 0; }
}

/* Done View */
.done-view {
  padding: 20px 16px;
}
.done-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.done-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}
.done-icon { font-size: 44px; }
.done-header h3 { color: #667eea; margin: 0; font-size: 14px; }
.done-header h4 { color: #333; margin: 4px 0 0; font-size: 18px; font-weight: 800; }
.done-body { margin-bottom: 20px; }
.done-field {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #f8f8f8;
  gap: 10px;
}
.done-label { font-size: 13px; color: #888; flex-shrink: 0; font-weight: 600; }
.done-value { font-size: 13px; color: #333; text-align: right; line-height: 1.5; }

/* All Done */
.all-done-card {
  background: white;
  border-radius: 20px;
  padding: 36px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.all-done-icon { font-size: 64px; display: block; margin-bottom: 12px; }
.all-done-card h3 { color: #333; margin: 0 0 6px; font-size: 18px; }
.all-done-card p { color: #888; font-size: 14px; margin: 0 0 10px; }

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
  padding: 5px 20px;
}
.nav-item.active { color: #667eea; font-weight: 700; }
.nav-item span:first-child { font-size: 22px; }

/* Quiz Section */
.quiz-section {
  margin: 0 16px 16px;
}
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #fff5f5, #fff0f0);
  border-radius: 14px;
  padding: 14px 18px;
  font-weight: 700;
  font-size: 15px;
  color: #333;
  border: 2px dashed #ffc9c9;
}
.quiz-status {
  font-size: 12px;
  font-weight: 600;
  color: #888;
}

.quiz-body {
  background: white;
  border-radius: 16px;
  padding: 16px;
  margin-top: 10px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
.quiz-tip {
  font-size: 13px;
  color: #888;
  margin: 0 0 14px;
  text-align: center;
}
.quiz-item {
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f0f0f0;
}
.quiz-q-title {
  font-size: 14px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px;
  line-height: 1.5;
}
.quiz-tf-badge {
  display: inline-block;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  margin-left: 6px;
  vertical-align: middle;
}
.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.quiz-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f5f7fb;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  font-size: 13px;
  color: #555;
}
.quiz-option:hover { background: #eef0ff; }
.quiz-option.selected {
  border-color: #667eea;
  background: #f0f4ff;
  color: #333;
}
.quiz-radio-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #ccc;
  flex-shrink: 0;
  transition: all 0.2s;
  position: relative;
}
.quiz-radio-dot.checked {
  border-color: #667eea;
  background: #667eea;
}
.quiz-radio-dot.checked::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  top: 4px;
  left: 4px;
}
.quiz-option input[type="radio"] {
  display: none;
}
.quiz-submit-btn {
  width: 100%;
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 8px;
  transition: all 0.2s;
}
.quiz-submit-btn:hover:not(:disabled) { transform: translateY(-2px); }
.quiz-submit-btn:disabled { opacity: 0.6; }

/* Quiz Results */
.quiz-result-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-top: 10px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
  text-align: center;
}
.quiz-score-circle {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  margin: 0 auto 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 5px solid;
}
.quiz-score-circle.pass { border-color: #2ed573; background: #f0fff4; }
.quiz-score-circle.fail { border-color: #ff6b6b; background: #fff5f5; }
.quiz-score-num { font-size: 28px; font-weight: 800; }
.quiz-score-circle.pass .quiz-score-num { color: #2ed573; }
.quiz-score-circle.fail .quiz-score-num { color: #ff6b6b; }
.quiz-score-label { font-size: 11px; color: #888; }
.quiz-result-detail { margin-bottom: 14px; }
.quiz-result-text { font-size: 14px; color: #333; margin: 0 0 8px; }
.quiz-retry-btn {
  background: #f0f0f0;
  border: none;
  padding: 8px 20px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  color: #555;
  transition: all 0.2s;
}
.quiz-retry-btn:hover { background: #ddd; }
.quiz-explanations {
  text-align: left;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}
.quiz-explain-item {
  display: flex;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #fafafa;
}
.quiz-explain-icon { font-size: 16px; flex-shrink: 0; margin-top: 2px; }
.quiz-explain-text p {
  font-size: 12px;
  color: #666;
  margin: 0 0 3px;
}
.quiz-explain-detail {
  color: #999;
  font-size: 11px;
  background: #f8f8f8;
  border-radius: 8px;
  padding: 6px 10px;
  margin-top: 4px;
}
</style>
