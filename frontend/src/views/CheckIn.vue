<template>
  <div class="checkin-page">
    <header class="top-bar">
      <button class="btn-back" @click="goHome">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
      </button>
      <h1 class="page-title">21天健康用网打卡</h1>
      <button class="btn-rules" @click="router.push('/rules')">打卡规则</button>
    </header>

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

    <div v-else>
      <!-- 个人信息/学号认证未完成拦截 -->
      <div v-if="!readyToCheckin" class="checkin-block">
        <div class="block-card">
          <div class="block-icon">🔒</div>
          <h2 class="block-title">尚未满足打卡条件</h2>
          <p class="block-desc">请先完成以下步骤后方可开始打卡：</p>
          <div class="block-steps">
            <div class="block-step" :class="{ done: profileReady, current: !profileReady }">
              <span class="step-num">{{ profileReady ? '✅' : '1' }}</span>
              <div>
                <span class="step-title">完善个人信息</span>
                <span class="step-desc" v-if="!profileReady">填写昵称、年龄、年级、性别</span>
              </div>
            </div>
            <div class="step-connector" :class="{ done: profileReady }"></div>
            <div class="block-step" :class="{ done: authReady, current: profileReady && !authReady }">
              <span class="step-num">{{ authReady ? '✅' : '2' }}</span>
              <div>
                <span class="step-title">学号认证</span>
                <span class="step-desc" v-if="!authReady && profileReady">提交学号信息并通过审核</span>
              </div>
            </div>
          </div>
          <button v-if="!profileReady" class="btn-block-action" @click="router.push('/my')">先去完善个人信息 →</button>
          <button v-else-if="!authReady" class="btn-block-action" @click="router.push('/auth')">去学号认证 →</button>
          <button v-else class="btn-block-action" @click="checkReadiness">刷新状态</button>
        </div>
      </div>

      <div v-else>
      <section class="hero-section">
        <div class="hero-content">
          <div class="hero-text">
            <h2 class="hero-title">21天健康用网</h2>
            <h3 class="hero-subtitle">打卡挑战</h3>
            <div class="hero-checkmark">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="#22c55e" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <p class="hero-desc">自律上网每一天 健康成长每一步</p>
          </div>
          <div class="hero-illustration">
            <img src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20cartoon%20boy%20holding%20smartphone%2C%20blue%20hoodie%2C%20happy%20expression%2C%20outdoor%20nature%20background%2C%20green%20trees%2C%20blue%20sky%2C%20simple%20flat%20illustration%2C%20health%20theme&image_size=portrait_4_3" alt="健康上网少年" />
          </div>
        </div>
      </section>

      <section class="progress-section">
        <div class="progress-card">
          <div class="progress-header">
            <span class="progress-label">我的打卡进度</span>
            <span class="progress-count">已坚持 {{ stats.total_days }} 天</span>
          </div>
          <div class="day-circles">
            <div
              v-for="day in 21"
              :key="day"
              class="day-circle"
              :class="{
                done: checkins[day],
                locked: !checkins[day] && day > maxAvailableDay,
                current: !checkins[day] && day === maxAvailableDay,
              }"
              @click="selectDayByNumber(day)"
            >
              <span v-if="checkins[day]" class="day-check">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </span>
              <span v-else class="day-num">{{ day }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="form-section" v-if="currentTopic">
        <div class="form-card">
          <div class="form-header">
            <span class="form-title">今日打卡（第{{ currentTopic.day }}天）</span>
            <span class="form-progress">{{ completedQuestions }}/5</span>
          </div>
          <p class="form-desc">请认真回答以下问题，记录你的今天吧~</p>

          <div v-if="currentQuestionIndex === 0" class="question-block">
            <div class="question-header">
              <span class="question-num">1</span>
              <span class="question-text">今天我使用网络的总时长大约是？</span>
              <span class="question-tag">单选</span>
            </div>
            <div class="option-grid">
              <label
                v-for="opt in durationOptions"
                :key="opt.value"
                class="option-item"
                :class="{ selected: form.online_duration === opt.value }"
              >
                <input type="radio" v-model="form.online_duration" :value="opt.value" hidden />
                <span class="option-letter">{{ opt.letter }}</span>
                <span class="option-label">{{ opt.label }}</span>
              </label>
            </div>
          </div>

          <div v-if="currentQuestionIndex === 1" class="question-block">
            <div class="question-header">
              <span class="question-num">2</span>
              <span class="question-text">我今天上网主要做了什么？（可多选）</span>
              <span class="question-tag">多选</span>
            </div>
            <div class="activity-grid">
              <label
                v-for="act in activityOptions"
                :key="act.value"
                class="activity-item"
                :class="{ selected: selectedActivities.includes(act.value) }"
                @click="toggleActivity(act.value)"
              >
                <span class="activity-icon">{{ act.icon }}</span>
                <span class="activity-label">{{ act.label }}</span>
                <span v-if="selectedActivities.includes(act.value)" class="activity-check">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </span>
              </label>
            </div>
          </div>

          <div v-if="currentQuestionIndex === 2" class="question-block">
            <div class="question-header">
              <span class="question-num">3</span>
              <span class="question-text">今天上网有没有影响到你的学习或生活？</span>
              <span class="question-tag">单选</span>
            </div>
            <div class="option-grid">
              <label
                v-for="opt in impactOptions"
                :key="opt.value"
                class="option-item"
                :class="{ selected: form.online_impact === opt.value }"
              >
                <input type="radio" v-model="form.online_impact" :value="opt.value" hidden />
                <span class="option-letter">{{ opt.letter }}</span>
                <span class="option-label">{{ opt.label }}</span>
              </label>
            </div>
          </div>

          <div v-if="currentQuestionIndex === 3" class="question-block">
            <div class="question-header">
              <span class="question-num">4</span>
              <span class="question-text">{{ currentTopic.title }}</span>
              <span class="question-tag"></span>
            </div>
            <div class="topic-question-box">
              <p>{{ currentTopic.question }}</p>
            </div>
            <textarea
              v-model="form.answer"
              class="question-textarea"
              placeholder="写下你的想法吧...（至少5个字）"
              rows="3"
            ></textarea>
          </div>

          <div v-if="currentQuestionIndex === 4" class="question-block">
            <div class="question-header">
              <span class="question-num">5</span>
              <span class="question-text">今天的心情</span>
              <span class="question-tag"></span>
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

          <div v-if="currentQuestionIndex >= 0 && currentQuestionIndex <= 3" class="question-nav">
            <button v-if="currentQuestionIndex > 0" class="btn-prev" @click="prevQuestion">上一题</button>
            <button class="btn-next" @click="nextQuestion" :disabled="!currentQuestionValid">
              {{ currentQuestionIndex === 3 ? '完成打卡' : '下一题' }}
            </button>
          </div>

          <div v-if="currentQuestionIndex === 4" class="question-nav">
            <button class="btn-prev" @click="prevQuestion">上一题</button>
            <button class="btn-submit" @click="handleSubmit" :disabled="submitting">
              {{ submitting ? '⏳ 提交中...' : '✅ 完成打卡，提交问卷' }}
            </button>
          </div>

          <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

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
        </div>
      </section>

      <section class="form-section" v-else-if="checkedInToday && !stats.completed">
        <div class="all-done-card" style="background: #f0fdf4; border: 2px solid #bbf7d0;">
          <span class="all-done-icon">✅</span>
          <h3>今日已打卡</h3>
          <p>今天已经打过卡了，明天再来继续吧～</p>
          <button class="btn-primary" @click="goHome">返回首页</button>
        </div>
      </section>

      <section class="form-section" v-else-if="stats.completed">
        <div class="all-done-card">
          <span class="all-done-icon">🏆</span>
          <h3>恭喜！21天全部完成！</h3>
          <p>你已经是网络安全小达人了！</p>
          <button class="btn-primary" @click="goHome">返回首页</button>
        </div>
      </section>

      <section class="form-section" v-else>
        <div class="all-done-card" style="background: #f0f4ff;">
          <span class="all-done-icon">☕</span>
          <h3>暂无打卡任务</h3>
          <p>休息一下，明天继续加油～</p>
          <button class="btn-primary" @click="goHome">返回首页</button>
        </div>
      </section>
    </div>
    </div>

    <BottomNav activeTab="checkin" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BottomNav from '../components/BottomNav.vue'
import { getTopics, submitCheckIn, getQuizQuestions, submitQuiz as submitQuizApi, getProfile } from '../api/index.js'
import { fetchCheckIns, fetchStats, checkinMap, stats as storeStats, invalidateCheckins } from '../stores/checkinStore.js'

const router = useRouter()
const route = useRoute()

const topics = ref([])
const checkins = checkinMap  // 共享缓存：{ [day]: record }
const stats = storeStats      // 共享缓存：{ total_days, streak_days, progress, completed }
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
const currentQuestionIndex = ref(0)
const checkedInToday = ref(false)
const readyToCheckin = ref(false)
const profileReady = ref(false)
const authReady = ref(false)

const form = reactive({
  online_duration: '',
  online_activities: '',
  online_impact: '',
  answer: '',
  mood: '😊',
})

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
    { id: -1, question: '以下哪个密码最安全？', options: { A: '123456', B: 'password', C: 'W@b#5e$8q', D: 'abcdef' }, answer: 'C', explanation: '包含大小写字母、数字和特殊符号的密码最安全', isDefault: true },
    { id: -2, question: '收到陌生人发来的链接应该怎么做？', options: { A: '直接点击', B: '先确认来源安全', C: '转发给朋友', D: '保存下来' }, answer: 'B', explanation: '陌生链接可能包含病毒，应先确认来源安全', isDefault: true },
    { id: -3, question: '在公共WiFi环境下，以下哪种做法最安全？', options: { A: '网上购物', B: '登录银行账户', C: '只浏览新闻', D: '发送密码' }, answer: 'C', explanation: '公共WiFi下只适合浏览公开内容', isDefault: true },
    { id: -4, question: '网络诈骗通常会用什么方式引诱你？', options: { A: '告诉你中大奖', B: '要求转账', C: '冒充客服', D: '以上都是' }, answer: 'D', explanation: '这些都是常见的诈骗手法', isDefault: true },
    { id: -5, question: '个人隐私信息包括哪些？', options: { A: '手机号', B: '学号', C: '家庭住址', D: '以上都是' }, answer: 'D', explanation: '手机号、学号、家庭住址都是重要的隐私信息', isDefault: true },
    { id: -6, question: '遇到网络暴力应该怎么做？', options: { A: '互骂回去', B: '沉默忍受', C: '保留证据并举报', D: '告诉所有人' }, answer: 'C', explanation: '保留证据并举报是最正确的处理方式', isDefault: true },
    { id: -7, question: '密码应该多长时间更换一次？', options: { A: '从不更换', B: '半年一次', C: '一年一次', D: '三个月一次' }, answer: 'D', explanation: '建议每三个月更换一次密码', isDefault: true },
    { id: -8, question: '钓鱼网站的特征是什么？', options: { A: '网址很像正规网站', B: '要求输入账号密码', C: '页面粗糙', D: '以上都是' }, answer: 'D', explanation: '这些都是钓鱼网站常见特征', isDefault: true },
    { id: -9, question: '游戏中陌生人要你充值应该怎么做？', options: { A: '立即充值', B: '拒绝并举报', C: '先充一点试试', D: '借给他钱' }, answer: 'B', explanation: '应拒绝陌生人的充值要求并举报', isDefault: true },
    { id: -10, question: '刷短视频遇到不良内容应该？', options: { A: '继续看', B: '举报并屏蔽', C: '分享给别人', D: '下载保存' }, answer: 'B', explanation: '遇到不良内容应举报并屏蔽', isDefault: true },
    { id: -11, question: '以下哪个是健康的上网习惯？', options: { A: '通宵上网', B: '定时休息远眺', C: '边吃饭边看屏幕', D: '走路看手机' }, answer: 'B', explanation: '定时休息远眺有助于保护视力', isDefault: true },
    { id: -12, question: '网友约你见面应该怎么做？', options: { A: '立刻答应', B: '独自赴约', C: '告诉家长并拒绝', D: '偷偷去' }, answer: 'C', explanation: '未成年人不应与网友私下见面', isDefault: true },
    { id: -13, question: '手机收到陌生链接应该？', options: { A: '点开看看', B: '转发给朋友', C: '不点击并删除', D: '回复问是谁' }, answer: 'C', explanation: '陌生链接可能含有病毒或钓鱼页面', isDefault: true },
    { id: -14, question: '以下哪种做法能保护个人隐私？', options: { A: '所有平台用同一密码', B: '不随意透露个人信息', C: '把密码告诉好友', D: '用生日做密码' }, answer: 'B', explanation: '不随意透露个人信息是保护隐私的基本做法', isDefault: true },
    { id: -15, question: '发现网上有人散布谣言应该？', options: { A: '帮忙转发', B: '不传谣并举报', C: '相信并告诉别人', D: '不管' }, answer: 'B', explanation: '不信谣不传谣，并积极举报', isDefault: true },
  ]
  const startIdx = ((day - 1) * 5) % defaultQuizzes.length
  const selected = []
  for (let i = 0; i < 5; i++) {
    selected.push(defaultQuizzes[(startIdx + i) % defaultQuizzes.length])
  }
  quizQuestions.value = selected.map(q => ({ id: q.id, question: q.question, options: q.options, answer: q.answer, explanation: q.explanation, isDefault: true }))
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

  const day = currentDay.value || (stats.total_days + 1)

  // 默认题目（本地题库）：前端直接判断对错，不请求后端
  if (quizQuestions.value.length > 0 && quizQuestions.value[0].isDefault) {
    let correctCount = 0
    const results = quizQuestions.value.map(q => {
      const userAnswer = quizAnswerMap.value[q.id]
      const isCorrect = q.answer === userAnswer
      if (isCorrect) correctCount++
      return {
        id: q.id, question: q.question, q_type: 'choice',
        user_answer: userAnswer, correct_answer: q.answer,
        is_correct: isCorrect, explanation: q.explanation || '',
      }
    })
    const total = quizQuestions.value.length
    const score = Math.round(correctCount / total * 100)
    quizResult.value = { total, correct: correctCount, score, results }
    quizSubmitted.value = true
    return
  }

  // 服务端题目：提交到后端评分
  const answers = quizQuestions.value.map(q => ({ id: q.id, answer: quizAnswerMap.value[q.id] }))
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
  loadQuiz()
}

const durationOptions = [
  { letter: 'A', value: '少于1小时', label: '少于1小时' },
  { letter: 'B', value: '1-2小时', label: '1-2小时' },
  { letter: 'C', value: '2-3小时', label: '2-3小时' },
  { letter: 'D', value: '超过3小时', label: '超过3小时' },
]

const activityOptions = [
  { value: '学习查资料', label: '学习/查资料', icon: '📚' },
  { value: '听音乐看视频', label: '听音乐/看视频', icon: '🎵' },
  { value: '社交聊天', label: '社交聊天', icon: '💬' },
  { value: '玩游戏', label: '玩游戏', icon: '🎮' },
  { value: '浏览新闻资讯', label: '浏览新闻/资讯', icon: '📰' },
  { value: '其他', label: '其他', icon: '📌' },
]

const impactOptions = [
  { letter: 'A', value: '没有影响', label: '没有影响' },
  { letter: 'B', value: '轻微影响', label: '轻微影响' },
  { letter: 'C', value: '有些影响', label: '有些影响' },
  { letter: 'D', value: '严重影响', label: '严重影响' },
]

const moods = ['😊', '😄', '🥰', '🤩', '😎', '🤗', '💪', '🔥', '😅', '🤔']

const maxAvailableDay = computed(() => {
  const maxChecked = Math.max(0, ...Object.keys(checkins.value).map(Number))
  return Math.min(maxChecked + 1, 21)
})

const currentTopic = computed(() => {
  if (checkedInToday.value) return null
  const targetDay = currentDay.value || maxAvailableDay.value
  if (!targetDay || targetDay > 21) return null
  if (checkins.value[targetDay]) return null
  return topics.value.find(t => t.day === targetDay)
})

const completedQuestions = computed(() => {
  let count = 0
  if (form.online_duration) count++
  if (selectedActivities.value.length > 0) count++
  if (form.online_impact) count++
  if (form.answer.trim()) count++
  if (form.mood) count++
  return count
})

const currentQuestionValid = computed(() => {
  if (currentQuestionIndex.value === 0) return !!form.online_duration
  if (currentQuestionIndex.value === 1) return selectedActivities.value.length > 0
  if (currentQuestionIndex.value === 2) return !!form.online_impact
  if (currentQuestionIndex.value === 3) return form.answer.trim().length >= 5
  if (currentQuestionIndex.value === 4) return !!form.mood
  return false
})

function toggleActivity(val) {
  const idx = selectedActivities.value.indexOf(val)
  if (idx >= 0) {
    selectedActivities.value.splice(idx, 1)
  } else {
    selectedActivities.value.push(val)
  }
  form.online_activities = selectedActivities.value.join('、')
}

function selectDayByNumber(day) {
  if (checkins.value[day]) {
    const topic = topics.value.find(t => t.day === day)
    if (topic) {
      viewingRecord.value = {
        ...checkins.value[day],
        icon: topic.icon,
        title: topic.title,
      }
    }
    return
  }
  if (day > maxAvailableDay.value) return
  viewingRecord.value = null
  currentDay.value = day
  resetForm()
  currentQuestionIndex.value = 0
  loadQuiz()
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

function prevQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

function nextQuestion() {
  if (!currentQuestionValid.value) return
  if (currentQuestionIndex.value < 4) {
    currentQuestionIndex.value++
  }
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

async function checkReadiness() {
  try {
    const res = await getProfile()
    const p = res.data
    profileReady.value = !!(p.nickname && p.age && p.grade && p.gender)
    authReady.value = p.auth_status === 'approved'
    readyToCheckin.value = profileReady.value && authReady.value
  } catch (e) {
    console.error('检查打卡资格失败:', e)
  }
}

async function loadData() {
  try {
    const [topicsRes] = await Promise.all([
      getTopics(),
      fetchCheckIns(),
      fetchStats(),
    ])
    topics.value = topicsRes.data

    // 检查今天是否已经打过卡
    const todayStr = new Date().toISOString().split('T')[0]
    checkedInToday.value = Object.values(checkins.value).some(r => r.date === todayStr)
  } catch (e) {
    console.error(e)
  }
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!form.online_duration) {
    errorMsg.value = '请选择今日上网时长'
    currentQuestionIndex.value = 0
    return
  }
  if (selectedActivities.value.length === 0) {
    errorMsg.value = '请至少选择一项上网活动'
    currentQuestionIndex.value = 1
    return
  }
  if (!form.online_impact) {
    errorMsg.value = '请选择上网带来的影响'
    currentQuestionIndex.value = 2
    return
  }
  if (!form.answer.trim() || form.answer.trim().length < 5) {
    errorMsg.value = '请认真回答思考题（至少5个字）'
    currentQuestionIndex.value = 3
    return
  }

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
      online_impact: form.online_impact,
      mood: form.mood,
    })
    const data = res.data

    // 更新本地缓存
    checkins.value[day] = data.record
    stats.value.total_days = (stats.value.total_days || 0) + 1
    stats.value.progress = Math.round(stats.value.total_days / 21 * 100)
    if (stats.value.total_days > (stats.value.streak_days || 0)) {
      stats.value.streak_days = stats.value.total_days
    }
    checkedInToday.value = true

    // 使共享缓存失效，确保其他页面刷新数据
    invalidateCheckins()

    lastSubmit.duration = form.online_duration
    lastSubmit.activities = form.online_activities
    lastSubmit.mood = form.mood
    successDay.value = day
    successCount.value = stats.value.total_days
    successPercent.value = stats.value.progress
    submitted.value = true

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
  await checkReadiness()
  if (readyToCheckin.value) {
    await loadData()
    loadQuiz()
  }
})
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background: var(--bg-gradient);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 打卡拦截提示 */
.checkin-block {
  padding: 40px 16px;
}
.block-card {
  background: white;
  border-radius: 20px;
  padding: 32px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.block-icon { font-size: 48px; margin-bottom: 12px; }
.block-title { font-size: 20px; font-weight: 800; color: #333; margin: 0 0 8px; }
.block-desc { font-size: 14px; color: #666; margin: 0 0 24px; }
.block-steps { margin-bottom: 24px; }
.block-step {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: #f8f9fa;
  margin-bottom: 0;
  text-align: left;
}
.block-step.done { background: #f0fdf4; }
.block-step.current { background: #eff6ff; border: 2px solid var(--color-primary); }
.step-num {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: #666;
  flex-shrink: 0;
}
.block-step.current .step-num { background: var(--color-primary); color: white; }
.block-step.done .step-num { background: #22c55e; }
.step-title { font-size: 15px; font-weight: 700; color: #333; display: block; }
.step-desc { font-size: 12px; color: #999; margin-top: 2px; display: block; }
.step-connector {
  width: 2px; height: 20px;
  background: #e5e7eb;
  margin-left: 31px;
}
.step-connector.done { background: #22c55e; }
.btn-block-action {
  width: 100%;
  background: var(--gradient-primary);
  color: white; border: none;
  padding: 14px; border-radius: 14px;
  font-size: 16px; font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-block-action:hover { transform: translateY(-2px); }

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
  background: none;
  border: none;
  color: #333;
  cursor: pointer;
  padding: 6px;
  border-radius: 10px;
  transition: background 0.2s;
}
.btn-back:hover { background: #f0f0f0; }
.page-title {
  font-size: 17px;
  font-weight: 700;
  color: #333;
  margin: 0;
}
.btn-rules {
  background: none;
  border: none;
  color: #1E90FF;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 10px;
  transition: background 0.2s;
}
.btn-rules:hover { background: #e6f2ff; }

.hero-section {
  padding: 20px 16px;
  position: relative;
}
.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='20' cy='30' r='4' fill='white' opacity='0.6'/%3E%3Ccircle cx='60' cy='20' r='6' fill='white' opacity='0.5'/%3E%3Ccircle cx='80' cy='40' r='3' fill='white' opacity='0.7'/%3E%3C/svg%3E");
  background-size: 200px 200px;
}
.hero-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}
.hero-text {
  flex: 1;
  padding-right: 16px;
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
.hero-checkmark {
  display: inline-block;
  background: #22c55e;
  border-radius: 50%;
  padding: 4px;
  margin-left: 8px;
  vertical-align: middle;
}
.hero-desc {
  font-size: 13px;
  color: #555;
  margin: 8px 0 0;
  font-weight: 500;
}
.hero-illustration {
  width: 120px;
  height: 120px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.hero-illustration img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.progress-section {
  padding: 0 16px;
  margin-bottom: 16px;
}
.progress-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.progress-label {
  font-size: 15px;
  font-weight: 700;
  color: #333;
}
.progress-count {
  font-size: 14px;
  font-weight: 600;
  color: #1E90FF;
}
.day-circles {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.day-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}
.day-circle:hover {
  transform: scale(1.1);
}
.day-circle.done {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}
.day-circle.current {
  background: var(--gradient-primary);
  animation: pulse 1.5s infinite;
}
.day-circle.locked {
  opacity: 0.4;
  cursor: not-allowed;
}
.day-num {
  font-size: 13px;
  font-weight: 700;
  color: #888;
}
.day-circle.done .day-num { color: white; }
.day-circle.current .day-num { color: white; }
.day-check {
  display: flex;
  align-items: center;
  justify-content: center;
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(59, 130, 246, 0); }
}

.form-section {
  padding: 0 16px;
}
.form-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.form-title {
  font-size: 16px;
  font-weight: 700;
  color: #333;
}
.form-progress {
  font-size: 14px;
  font-weight: 700;
  color: #1E90FF;
}
.form-desc {
  font-size: 13px;
  color: #888;
  margin: 0 0 20px;
}

.question-block {
  margin-bottom: 24px;
}
.question-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}
.question-num {
  width: 28px;
  height: 28px;
  background: var(--gradient-primary);
  border-radius: 50%;
  color: white;
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.question-text {
  font-size: 15px;
  font-weight: 700;
  color: #333;
  flex: 1;
}
.question-tag {
  font-size: 11px;
  color: white;
  background: var(--color-primary);
  padding: 2px 8px;
  border-radius: 8px;
  font-weight: 600;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #f8fafc;
  border-radius: 14px;
  padding: 14px 12px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}
.option-item:hover {
  background: #f0f4ff;
}
.option-item.selected {
  background: #eff6ff;
  border-color: var(--color-primary);
}
.option-letter {
  width: 28px;
  height: 28px;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
}
.option-item.selected .option-letter {
  background: var(--color-primary);
  color: white;
}
.option-label {
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}
.option-item.selected .option-label {
  color: #1e40af;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.activity-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: #f8fafc;
  border-radius: 14px;
  padding: 14px 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  position: relative;
}
.activity-item:hover {
  background: #f0f4ff;
}
.activity-item.selected {
  background: #eff6ff;
  border-color: var(--color-primary);
}
.activity-icon {
  font-size: 24px;
}
.activity-label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
  text-align: center;
}
.activity-item.selected .activity-label {
  color: #1e40af;
}
.activity-check {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 18px;
  height: 18px;
  background: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.topic-question-box {
  background: #eff6ff;
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
}
.topic-question-box p {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  margin: 0;
}
.question-textarea {
  width: 100%;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  padding: 14px;
  font-size: 14px;
  resize: none;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color 0.2s;
}
.question-textarea:focus {
  border-color: var(--color-primary);
}

.mood-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.mood-option {
  font-size: 32px;
  cursor: pointer;
  padding: 6px;
  border-radius: 14px;
  transition: all 0.2s;
  opacity: 0.5;
}
.mood-option.selected, .mood-option:hover {
  opacity: 1;
  transform: scale(1.2);
  background: #eff6ff;
}

.question-nav {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}
.btn-prev {
  flex: 1;
  background: #f1f5f9;
  color: #475569;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-prev:hover {
  background: #e2e8f0;
}
.btn-next {
  flex: 2;
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-next:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}
.btn-next:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-submit {
  flex: 2;
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}
.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-text {
  color: #dc2626;
  font-size: 13px;
  text-align: center;
  margin: 12px 0;
}

.quiz-section {
  margin: 20px 0 0;
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
  background: #f8fafc;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
  font-size: 13px;
  color: #555;
}
.quiz-option:hover { background: #eff6ff; }
.quiz-option.selected {
  border-color: var(--color-primary);
  background: #eff6ff;
  color: #333;
}
.quiz-radio-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
  flex-shrink: 0;
  transition: all 0.2s;
  position: relative;
}
.quiz-radio-dot.checked {
  border-color: var(--color-primary);
  background: var(--color-primary);
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
.quiz-score-circle.pass { border-color: #22c55e; background: #f0fff4; }
.quiz-score-circle.fail { border-color: #dc2626; background: #fff5f5; }
.quiz-score-num { font-size: 28px; font-weight: 800; }
.quiz-score-circle.pass .quiz-score-num { color: #22c55e; }
.quiz-score-circle.fail .quiz-score-num { color: #dc2626; }
.quiz-score-label { font-size: 11px; color: #888; }
.quiz-result-detail { margin-bottom: 14px; }
.quiz-result-text { font-size: 14px; color: #333; margin: 0 0 8px; }
.quiz-retry-btn {
  background: #f1f5f9;
  border: none;
  padding: 8px 20px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  color: #475569;
  transition: all 0.2s;
}
.quiz-retry-btn:hover { background: #e2e8f0; }
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
  background: #f8fafc;
  border-radius: 8px;
  padding: 6px 10px;
  margin-top: 4px;
}

.btn-primary {
  width: 100%;
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 16px;
  transition: all 0.2s;
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.all-done-card {
  background: white;
  border-radius: 20px;
  padding: 36px 24px;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.all-done-icon { font-size: 64px; display: block; margin-bottom: 12px; }
.all-done-card h3 { color: #333; margin: 0 0 6px; font-size: 18px; }
.all-done-card p { color: #888; font-size: 14px; margin: 0 0 10px; }

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
  background: linear-gradient(135deg, #22c55e, #16a34a);
  border-radius: 50%; display: flex;
  align-items: center; justify-content: center;
  animation: pulse 0.6s infinite alternate;
}
.success-emoji { font-size: 40px; }
.success-modal h2 {
  color: #22c55e; margin: 0 0 8px; font-size: 24px; font-weight: 800;
}
.success-badge {
  display: inline-block; background: var(--gradient-primary);
  color: white; font-size: 13px; padding: 4px 16px;
  border-radius: 20px; font-weight: 700; margin-bottom: 8px;
}
.success-msg { color: #666; font-size: 14px; margin: 0 0 16px; }
.progress-mini {
  height: 8px;
  background: #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 12px;
}
.progress-mini-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  border-radius: 8px;
  transition: width 0.8s ease;
}
.success-detail {
  margin: 12px 0;
  background: #f8fafc;
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

.done-view {
  padding: 20px 16px;
}
.done-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.done-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}
.done-icon { font-size: 44px; }
.done-header h3 { color: var(--color-primary); margin: 0; font-size: 14px; }
.done-header h4 { color: #333; margin: 4px 0 0; font-size: 18px; font-weight: 800; }
.done-body { margin-bottom: 20px; }
.done-field {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #f8fafc;
  gap: 10px;
}
.done-label { font-size: 13px; color: #888; flex-shrink: 0; font-weight: 600; }
.done-value { font-size: 13px; color: #333; text-align: right; line-height: 1.5; }
</style>