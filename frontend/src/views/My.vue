<template>
  <div class="my-page">
    <!-- Header -->
    <header class="header">
      <span class="header-avatar">{{ form.avatar || '🧒' }}</span>
      <div class="header-info">
        <h2>{{ form.nickname || '未设置昵称' }}</h2>
        <span class="header-phone">{{ form.phone }}</span>
      </div>
    </header>

    <!-- Tab切换 -->
    <div class="tab-bar">
      <button class="tab-item" :class="{ active: activeTab === 'profile' }" @click="activeTab = 'profile'">
        <span>👤</span><span>个人资料</span>
      </button>
      <button class="tab-item" :class="{ active: activeTab === 'badges' }" @click="activeTab = 'badges'">
        <span>🏅</span><span>成就徽章</span>
      </button>
      <button class="tab-item" :class="{ active: activeTab === 'settings' }" @click="activeTab = 'settings'">
        <span>⚙️</span><span>系统设置</span>
      </button>
    </div>

    <!-- ===== 个人资料 ===== -->
    <div v-if="activeTab === 'profile'" class="tab-content">
      <div class="panel">
        <h3 class="panel-title">基本信息</h3>

        <!-- 头像选择 -->
        <div class="field">
          <label>我的头像</label>
          <div class="avatar-grid">
            <span v-for="a in avatars" :key="a" class="avatar-option"
              :class="{ selected: form.avatar === a }"
              @click="form.avatar = a">{{ a }}</span>
          </div>
        </div>

        <!-- 昵称 -->
        <div class="field">
          <label>昵称</label>
          <input v-model="form.nickname" class="field-input" placeholder="给自己起个好听的名字" maxlength="20" />
        </div>

        <!-- 性别 -->
        <div class="field">
          <label>性别</label>
          <div class="gender-options">
            <button class="gender-btn" :class="{ selected: form.gender === '男' }" @click="form.gender = '男'">👦 男</button>
            <button class="gender-btn" :class="{ selected: form.gender === '女' }" @click="form.gender = '女'">👧 女</button>
            <button class="gender-btn" :class="{ selected: form.gender === '' }" @click="form.gender = ''">🔒 保密</button>
          </div>
        </div>

        <!-- 年龄 -->
        <div class="field">
          <label>年龄</label>
          <input v-model.number="form.age" class="field-input" type="number" min="6" max="25" placeholder="输入年龄" />
        </div>

        <!-- 年级 -->
        <div class="field">
          <label>年级</label>
          <select v-model="form.grade" class="field-input">
            <option value="">请选择年级</option>
            <option v-for="g in grades" :key="g" :value="g">{{ g }}</option>
          </select>
        </div>

        <!-- 手机号（只读） -->
        <div class="field">
          <label>手机号</label>
          <input :value="form.phone" class="field-input" disabled />
        </div>

        <!-- 保存按钮 -->
        <button class="btn-save" @click="saveProfile" :disabled="saving">
          {{ saving ? '保存中...' : '保存修改 ✅' }}
        </button>
        <p v-if="saveMsg" class="save-msg" :class="{ ok: saveOk }">{{ saveMsg }}</p>
      </div>

      <!-- 学号认证引导提示 -->
      <div v-if="profileComplete && authStatus !== 'approved' && authStatus !== 'pending'" class="auth-guide-banner">
        <span>🎓</span>
        <span>个人信息已完善！请完成<strong>学号认证</strong>后即可开始打卡</span>
      </div>

      <!-- 实名认证卡片 -->
      <div class="panel auth-panel">
        <div class="auth-header">
          <span class="auth-icon">🆔</span>
          <span class="auth-title">实名认证</span>
          <span class="auth-status" :class="authStatusClass">{{ authStatusText }}</span>
        </div>
        <p class="auth-desc">{{ authStatusDesc }}</p>
        <button class="auth-btn" @click="router.push('/auth')">
          {{ authBtnText }}
        </button>
      </div>
    </div>

    <!-- ===== 成就徽章 ===== -->
    <div v-if="activeTab === 'badges'" class="tab-content">
      <!-- 进度 -->
      <div class="panel">
        <div class="badge-summary">
          <div class="bs-item">
            <span class="bs-num">{{ achievements.unlocked_count || 0 }}</span>
            <span class="bs-label">已获得</span>
          </div>
          <div class="bs-item">
            <span class="bs-num">{{ achievements.total_badges || 9 }}</span>
            <span class="bs-label">总徽章</span>
          </div>
          <div class="bs-item">
            <span class="bs-num">{{ achievements.streak || 0 }}天</span>
            <span class="bs-label">连续打卡</span>
          </div>
        </div>
        <div class="badge-progress">
          <div class="badge-progress-fill"
            :style="{ width: ((achievements.unlocked_count || 0) / (achievements.total_badges || 1) * 100) + '%' }">
          </div>
        </div>
      </div>

      <!-- 已解锁 -->
      <div class="panel" v-if="unlockedBadges.length > 0">
        <h3 class="panel-title">
          <span class="panel-icon">🎖️</span>已解锁徽章
        </h3>
        <div class="badge-grid">
          <div v-for="b in unlockedBadges" :key="b.id" class="badge-card unlocked">
            <span class="badge-icon" :style="{ '--badge-color': b.color }">{{ b.icon }}</span>
            <span class="badge-name">{{ b.name }}</span>
            <span class="badge-desc">{{ b.desc }}</span>
          </div>
        </div>
      </div>

      <!-- 未解锁 -->
      <div class="panel" v-if="lockedBadges.length > 0">
        <h3 class="panel-title">
          <span class="panel-icon">🔒</span>待解锁徽章
        </h3>
        <div class="badge-grid">
          <div v-for="b in lockedBadges" :key="b.id" class="badge-card locked">
            <span class="badge-icon locked-icon">🔒</span>
            <span class="badge-name">{{ b.name }}</span>
            <span class="badge-desc">{{ b.desc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 系统设置 ===== -->
    <div v-if="activeTab === 'settings'" class="tab-content">
      <!-- 打卡提醒 -->
      <div class="panel">
        <h3 class="panel-title">
          <span class="panel-icon">🔔</span>打卡提醒
        </h3>
        <div class="settings-item">
          <div class="si-left">
            <span class="si-title">每日打卡提醒</span>
            <span class="si-desc">每天18:00提醒打卡</span>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="settings.reminder" @change="saveSettings" />
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>

      <!-- 隐私设置 -->
      <div class="panel">
        <h3 class="panel-title">
          <span class="panel-icon">🔐</span>隐私设置
        </h3>
        <button class="settings-btn" @click="router.push('/privacy')">
          <span>🔐</span><span>隐私与通知设置</span><span class="btn-arrow">›</span>
        </button>
      </div>

      <!-- 其他 -->
      <div class="panel">
        <h3 class="panel-title">
          <span class="panel-icon">📋</span>其他
        </h3>
        <button class="settings-btn" @click="clearCache">
          <span>🗑️</span><span>清除缓存</span><span class="btn-arrow">›</span>
        </button>
        <button class="settings-btn" @click="router.push('/feedback')">
          <span>💬</span><span>意见反馈</span><span class="btn-arrow">›</span>
        </button>
        <button class="settings-btn" @click="router.push('/stats')">
          <span>📊</span><span>查看数据报告</span><span class="btn-arrow">›</span>
        </button>
        <button class="settings-btn" @click="router.push('/quiz-history')">
          <span>📝</span><span>答题历史记录</span><span class="btn-arrow">›</span>
        </button>
        <button class="settings-btn" @click="router.push('/auth')">
          <span>🆔</span><span>实名认证</span><span class="btn-arrow">›</span>
        </button>
        <button class="settings-btn danger" @click="logout">
          <span>🚪</span><span>退出登录</span><span class="btn-arrow">›</span>
        </button>
      </div>

    </div>

    <!-- 底部导航 -->
    <BottomNav activeTab="my" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BottomNav from '../components/BottomNav.vue'
import { getProfile, updateProfile, getAchievements } from '../api/index'
import { logout as userLogout, fetchProfile as userFetchProfile, user as userStoreUser } from '../stores/userStore'

const router = useRouter()
const activeTab = ref('profile')
const saving = ref(false)
const saveMsg = ref('')
const saveOk = ref(false)
const profileComplete = ref(false)
const achievements = reactive({})
const showFeedback = ref(false)

// 个人资料表单
const form = reactive({
  phone: '',
  nickname: '',
  avatar: '🧒',
  age: '',
  grade: '',
  gender: '',
})

// 认证状态
const authStatus = ref('unverified')

// 设置
const settings = reactive({
  reminder: true,
  showRecords: true,
  showNickname: true,
})

const avatars = ['🧒', '👦', '👧', '🦊', '🐱', '🐶', '🐼', '🐰', '🦁', '🦄', '🐸', '🐵']
const grades = [
  '一年级', '二年级', '三年级', '四年级', '五年级', '六年级',
  '初一', '初二', '初三', '高一', '高二', '高三', '大学', '其他',
]

const unlockedBadges = computed(() => (achievements.badges || []).filter(b => b.unlocked))
const lockedBadges = computed(() => (achievements.badges || []).filter(b => !b.unlocked))

const authStatusText = computed(() => {
  const map = {
    unverified: '未认证',
    pending: '审核中',
    approved: '已通过',
    rejected: '未通过',
  }
  return map[authStatus.value] || '未知'
})

const authStatusClass = computed(() => authStatus.value)

const authStatusDesc = computed(() => {
  const map = {
    unverified: '完成实名认证可获得完整功能权限',
    pending: '您的申请正在审核中，请耐心等待',
    approved: '恭喜！您已通过实名认证',
    rejected: '认证未通过，请修改信息后重新提交',
  }
  return map[authStatus.value] || ''
})

const authBtnText = computed(() => {
  const map = {
    unverified: '📤 去认证',
    pending: '⏳ 审核中',
    approved: '✅ 查看认证信息',
    rejected: '🔄 重新认证',
  }
  return map[authStatus.value] || '去认证'
})

async function loadProfile() {
  try {
    const res = await getProfile()
    const data = res.data
    form.phone = data.phone || ''
    form.nickname = data.nickname || ''
    form.avatar = data.avatar || '🧒'
    form.age = data.age || ''
    form.grade = data.grade || ''
    form.gender = data.gender || ''
    authStatus.value = data.auth_status || 'unverified'
    profileComplete.value = !!(data.nickname && data.age && data.grade && data.gender)
    // 同步到 userStore
    userStoreUser.value = { ...userStoreUser.value, ...data }
    localStorage.setItem('user', JSON.stringify(userStoreUser.value))
  } catch (e) {
    console.error(e)
  }
}

async function loadAchievements() {
  try {
    const res = await getAchievements()
    Object.assign(achievements, res.data)
  } catch (e) {
    console.error(e)
  }
}

async function saveProfile() {
  saving.value = true
  saveMsg.value = ''
  try {
    await updateProfile({
      nickname: form.nickname,
      avatar: form.avatar,
      age: form.age,
      grade: form.grade,
      gender: form.gender,
    })
    // 更新 userStore 中的 user 信息
    await userFetchProfile()

    profileComplete.value = true
    saveOk.value = true
    saveMsg.value = authStatus.value === 'approved' ? '保存成功！' : '保存成功！请完成学号认证后开始打卡'
    setTimeout(() => { saveMsg.value = '' }, 3000)

    // 如果个人信息已完善但未认证，自动跳转认证页
    if (authStatus.value !== 'approved') {
      setTimeout(() => { router.push('/auth') }, 1500)
    }
  } catch (e) {
    saveOk.value = false
    saveMsg.value = e.response?.data?.error || '保存失败'
  }
  saving.value = false
}

function saveSettings() {
  localStorage.setItem('user_settings', JSON.stringify(settings))
}

function clearCache() {
  // 保留用户数据，清理其他缓存
  const u = userStoreUser.value ? JSON.stringify(userStoreUser.value) : null
  const t = localStorage.getItem('token')
  localStorage.clear()
  if (u) localStorage.setItem('user', u)
  if (t) localStorage.setItem('token', t)
  saveMsg.value = '缓存已清除'
  saveOk.value = true
  setTimeout(() => { saveMsg.value = '' }, 2000)
}

function logout() {
  userLogout()
  router.push('/login')
}

onMounted(() => {
  loadProfile()
  loadAchievements()
  // 加载设置
  const saved = localStorage.getItem('user_settings')
  if (saved) Object.assign(settings, JSON.parse(saved))
})
</script>

<style scoped>
.my-page {
  min-height: 100vh;
  background: var(--bg-gradient);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px 16px;
  background: var(--gradient-primary);
  color: white;
}
.header-avatar { font-size: 48px; }
.header-info h2 { margin: 0; font-size: 20px; font-weight: 800; }
.header-phone { font-size: 13px; opacity: 0.85; }

/* Tab Bar */
.tab-bar {
  display: flex;
  background: white;
  padding: 6px 16px;
  gap: 4px;
  position: sticky;
  top: 0;
  z-index: 30;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: none;
  border: none;
  padding: 10px 6px;
  font-size: 13px;
  color: #888;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-item.active {
  background: #eff6ff;
  color: var(--color-primary);
  font-weight: 700;
}
.tab-item span:first-child { font-size: 16px; }

/* Panel */
.tab-content { padding: 12px 16px; }
.panel {
  background: white;
  border-radius: 20px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.panel-title {
  font-size: 15px;
  font-weight: 700;
  color: #333;
  margin: 0 0 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.panel-icon { font-size: 18px; }

/* Fields */
.field { margin-bottom: 16px; }
.field label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  margin-bottom: 6px;
}
.field-input {
  width: 100%;
  border: 2px solid #e8ecf4;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  background: #fafbfd;
  transition: border-color 0.2s;
}
.field-input:focus { border-color: var(--color-primary); }
.field-input:disabled { background: #f0f0f0; color: #999; }

/* Avatar Grid */
.avatar-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.avatar-option {
  font-size: 32px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  cursor: pointer;
  border: 2px solid transparent;
  background: #f5f7fb;
  transition: all 0.2s;
}
.avatar-option.selected {
  border-color: var(--color-primary);
  background: #eff6ff;
  transform: scale(1.1);
}

/* Gender */
.gender-options {
  display: flex;
  gap: 8px;
}
.gender-btn {
  flex: 1;
  background: #f5f7fb;
  border: 2px solid transparent;
  border-radius: 12px;
  padding: 10px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
  color: #888;
}
.gender-btn.selected {
  border-color: var(--color-primary);
  background: #eff6ff;
  color: var(--color-primary);
}

.btn-save {
  width: 100%;
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 8px;
}
.btn-save:disabled { opacity: 0.6; }
.save-msg {
  text-align: center;
  font-size: 13px;
  margin: 8px 0 0;
  color: var(--color-danger);
}
.save-msg.ok { color: var(--color-success); }

/* Badges */
.badge-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 12px;
}
.bs-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.bs-num { font-size: 24px; font-weight: 900; color: var(--color-primary); }
.bs-label { font-size: 11px; color: #888; margin-top: 2px; }
.badge-progress {
  height: 8px;
  background: #e8ecf4;
  border-radius: 8px;
  overflow: hidden;
}
.badge-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), #22c55e);
  border-radius: 8px;
  transition: width 0.8s;
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.badge-card {
  background: #f8f9fd;
  border-radius: 14px;
  padding: 14px 8px;
  text-align: center;
}
.badge-card.unlocked { background: linear-gradient(135deg, #eff6ff, #f0fff4); }
.badge-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 6px;
  filter: drop-shadow(0 2px 4px var(--badge-color));
}
.badge-icon.locked-icon {
  font-size: 30px;
  filter: grayscale(1);
  opacity: 0.5;
}
.badge-name { font-size: 12px; font-weight: 700; color: #333; display: block; }
.badge-desc { font-size: 10px; color: #999; display: block; margin-top: 2px; }

/* Settings */
.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}
.settings-item + .settings-item { border-top: 1px solid #f5f5f5; }
.si-left { display: flex; flex-direction: column; gap: 2px; }
.si-title { font-size: 14px; font-weight: 600; color: #333; }
.si-desc { font-size: 11px; color: #bbb; }

/* Toggle */
.toggle-switch { position: relative; width: 48px; height: 28px; flex-shrink: 0; }
.toggle-switch input { display: none; }
.toggle-slider {
  position: absolute;
  inset: 0;
  background: #ddd;
  border-radius: 14px;
  cursor: pointer;
  transition: 0.3s;
}
.toggle-slider::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.toggle-switch input:checked + .toggle-slider { background: var(--color-primary); }
.toggle-switch input:checked + .toggle-slider::after { left: 23px; }

.settings-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  padding: 14px 4px;
  font-size: 14px;
  color: #444;
  cursor: pointer;
  border-bottom: 1px solid #f8f8f8;
  font-weight: 600;
}
.settings-btn:last-child { border-bottom: none; }
.settings-btn.danger { color: #ff6b6b; }
.settings-btn span:first-child { font-size: 18px; }
.btn-arrow { margin-left: auto; font-size: 20px; color: #ccc; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}
.modal-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  width: 100%;
  max-width: 360px;
}
.modal-card h3 { margin: 0 0 14px; font-size: 17px; }
.feedback-input {
  width: 100%;
  border: 2px solid #e8ecf4;
  border-radius: 12px;
  padding: 12px;
  font-size: 14px;
  resize: none;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
}
.feedback-input:focus { border-color: var(--color-primary); }
.modal-actions {
  display: flex;
  gap: 10px;
  margin-top: 14px;
}
.modal-btn {
  flex: 1;
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
}
.modal-btn.cancel { background: #f5f5f5; color: #888; }
.modal-btn.confirm { background: var(--gradient-primary); color: white; }
.modal-btn.confirm:disabled { opacity: 0.5; }
.feedback-ok { text-align: center; color: var(--color-success); font-size: 13px; margin: 10px 0 0; }

/* 学号认证引导横幅 */
.auth-guide-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--gradient-primary);
  color: white;
  padding: 12px 16px;
  border-radius: 14px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  animation: guidePulse 2s ease-in-out infinite;
}
.auth-guide-banner span:first-child {
  font-size: 22px;
}
@keyframes guidePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(37, 99, 235, 0); }
}

/* 实名认证卡片 */
.auth-panel {
  border: 2px solid #f0f0f0;
  background: linear-gradient(135deg, #f8f9ff, #fff5f8);
}
.auth-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.auth-icon { font-size: 20px; }
.auth-title {
  font-size: 15px;
  font-weight: 800;
  color: #333;
}
.auth-status {
  margin-left: auto;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
}
.auth-status.unverified {
  background: #f5f5f5;
  color: #999;
}
.auth-status.pending {
  background: #fffbf0;
  color: #ffa502;
}
.auth-status.approved {
  background: #f0fff4;
  color: var(--color-success);
}
.auth-status.rejected {
  background: #fff5f5;
  color: #ff6b6b;
}
.auth-desc {
  font-size: 13px;
  color: #666;
  margin: 0 0 14px;
}
.auth-btn {
  width: 100%;
  background: var(--gradient-primary);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s;
}
.auth-btn:hover {
  transform: translateY(-1px);
}
</style>
