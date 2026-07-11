<template>
  <div class="auth-page">
    <header class="top-bar">
      <button class="btn-back" @click="router.back()">
        <span>←</span><span>返回</span>
      </button>
      <div class="top-title">实名认证</div>
      <div class="top-placeholder"></div>
    </header>

    <div class="status-section" v-if="profile">
      <div class="status-card" :class="profile.auth_status">
        <div class="status-icon">
          <span v-if="profile.auth_status === 'unverified'">📝</span>
          <span v-else-if="profile.auth_status === 'pending'">⏳</span>
          <span v-else-if="profile.auth_status === 'approved'">✅</span>
          <span v-else>❌</span>
        </div>
        <div class="status-info">
          <h2>{{ statusText }}</h2>
          <p>{{ statusDesc }}</p>
        </div>
      </div>
    </div>

    <div class="form-section" v-if="showForm">
      <div class="form-card">
        <h3 class="form-title">填写认证信息</h3>
        <p class="form-tip">请如实填写以下信息，审核通过后将获得完整功能权限</p>
        
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">
              <span>👤</span><span>真实姓名</span>
              <span class="required">*</span>
            </label>
            <input
              v-model="form.real_name"
              type="text"
              class="form-input"
              placeholder="请输入真实姓名"
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span>🏫</span><span>学校名称</span>
              <span class="required">*</span>
            </label>
            <input
              v-model="form.school"
              type="text"
              class="form-input"
              placeholder="请输入学校名称"
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span>📚</span><span>班级</span>
              <span class="required">*</span>
            </label>
            <input
              v-model="form.class_name"
              type="text"
              class="form-input"
              placeholder="请输入班级（如：三年级二班）"
            />
          </div>

          <div class="form-group">
            <label class="form-label">
              <span>🆔</span><span>身份证号</span>
              <span class="required">*</span>
            </label>
            <input
              v-model="form.id_card"
              type="text"
              class="form-input"
              placeholder="请输入18位身份证号"
              maxlength="18"
            />
            <p class="form-hint">您的身份证号将被加密保存，仅用于身份验证</p>
          </div>

          <div v-if="profile.auth_status === 'rejected'" class="reject-info">
            <span class="reject-icon">💡</span>
            <span class="reject-text">上次审核未通过原因：{{ profile.auth_reason }}</span>
          </div>

          <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>

          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? '⏳ 提交中...' : '📤 提交认证申请' }}
          </button>
        </form>
      </div>
    </div>

    <div class="info-section" v-if="profile && profile.auth_status === 'approved'">
      <div class="info-card">
        <h3 class="info-title">认证信息</h3>
        <div class="info-item">
          <span class="info-label">真实姓名</span>
          <span class="info-value">{{ profile.real_name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">学校</span>
          <span class="info-value">{{ profile.school }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">班级</span>
          <span class="info-value">{{ profile.class_name }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">身份证号</span>
          <span class="info-value">{{ maskIdCard(profile.id_card) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">审核时间</span>
          <span class="info-value">{{ formatDate(profile.auth_time) }}</span>
        </div>
      </div>
    </div>

    <div class="tips-section">
      <div class="tips-card">
        <h4>📌 温馨提示</h4>
        <ul>
          <li>请确保填写的信息真实有效</li>
          <li>审核通常在1-3个工作日内完成</li>
          <li>审核结果将通过消息通知告知</li>
          <li>如信息有误可重新提交申请</li>
        </ul>
      </div>
    </div>

    <nav class="bottom-nav">
      <button class="nav-item" @click="router.push('/')">
        <span>🏠</span><span>首页</span>
      </button>
      <button class="nav-item" @click="router.push('/checkin')">
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
import { useRouter } from 'vue-router'
import { getProfile, submitAuth } from '../api/index.js'

const router = useRouter()

const profile = ref(null)
const submitting = ref(false)
const errorMsg = ref('')

const form = reactive({
  real_name: '',
  school: '',
  class_name: '',
  id_card: '',
})

const statusText = computed(() => {
  if (!profile.value) return '加载中...'
  const map = {
    unverified: '未认证',
    pending: '审核中',
    approved: '已通过',
    rejected: '未通过',
  }
  return map[profile.value.auth_status] || '未知'
})

const statusDesc = computed(() => {
  if (!profile.value) return ''
  const map = {
    unverified: '请填写真实信息完成实名认证',
    pending: '您的申请正在审核中，请耐心等待',
    approved: '恭喜！您已通过实名认证',
    rejected: '认证未通过，请修改信息后重新提交',
  }
  return map[profile.value.auth_status] || ''
})

const showForm = computed(() => {
  if (!profile.value) return false
  return profile.value.auth_status === 'unverified' || profile.value.auth_status === 'rejected'
})

function maskIdCard(id) {
  if (!id || id.length !== 18) return ''
  return id.slice(0, 4) + '**********' + id.slice(-4)
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

async function loadProfile() {
  try {
    const res = await getProfile()
    profile.value = res.data
    if (profile.value.auth_status === 'rejected') {
      form.real_name = profile.value.real_name || ''
      form.school = profile.value.school || ''
      form.class_name = profile.value.class_name || ''
      form.id_card = ''
    }
  } catch (e) {
    console.error('加载资料失败:', e)
  }
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!form.real_name.trim()) {
    errorMsg.value = '请输入真实姓名'
    return
  }
  if (!form.school.trim()) {
    errorMsg.value = '请输入学校名称'
    return
  }
  if (!form.class_name.trim()) {
    errorMsg.value = '请输入班级'
    return
  }
  if (!form.id_card.trim()) {
    errorMsg.value = '请输入身份证号'
    return
  }
  if (form.id_card.length !== 18) {
    errorMsg.value = '请输入有效的18位身份证号'
    return
  }

  submitting.value = true
  try {
    await submitAuth({
      real_name: form.real_name.trim(),
      school: form.school.trim(),
      class_name: form.class_name.trim(),
      id_card: form.id_card.trim(),
    })
    alert('认证申请已提交，等待管理员审核')
    await loadProfile()
  } catch (e) {
    const errData = e.response?.data
    errorMsg.value = errData?.error || '提交失败，请稍后重试'
  }
  submitting.value = false
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f9ff 0%, #fdf4ff 50%, #fef9c3 100%);
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

.status-section {
  padding: 20px 16px;
}

.status-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border-left: 6px solid;
}

.status-card.unverified {
  border-color: #999;
}

.status-card.pending {
  border-color: #ffa502;
  background: #fffbf0;
}

.status-card.approved {
  border-color: #2ed573;
  background: #f0fff4;
}

.status-card.rejected {
  border-color: #ff6b6b;
  background: #fff5f5;
}

.status-icon span {
  font-size: 40px;
}

.status-info h2 {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 800;
  color: #333;
}

.status-info p {
  margin: 0;
  font-size: 13px;
  color: #666;
}

.form-section, .info-section {
  padding: 0 16px;
  margin-bottom: 16px;
}

.form-card, .info-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.form-title, .info-title {
  font-size: 16px;
  font-weight: 800;
  color: #333;
  margin: 0 0 4px;
}

.form-tip {
  font-size: 12px;
  color: #999;
  margin: 0 0 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 700;
  color: #333;
  margin-bottom: 6px;
}

.form-label span:first-child {
  font-size: 16px;
}

.required {
  color: #ff6b6b;
  font-size: 12px;
}

.form-input {
  width: 100%;
  border: 2px solid #e8ecf4;
  border-radius: 12px;
  padding: 12px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #667eea;
}

.form-hint {
  font-size: 11px;
  color: #999;
  margin: 4px 0 0;
}

.reject-info {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #fff5f5;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 12px;
}

.reject-icon {
  font-size: 16px;
}

.reject-text {
  font-size: 12px;
  color: #ff6b6b;
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

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.6;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: #888;
  font-weight: 600;
}

.info-value {
  font-size: 13px;
  color: #333;
  font-weight: 700;
}

.tips-section {
  padding: 0 16px;
}

.tips-card {
  background: rgba(255,255,255,0.8);
  border-radius: 16px;
  padding: 16px;
}

.tips-card h4 {
  font-size: 14px;
  font-weight: 800;
  color: #333;
  margin: 0 0 10px;
}

.tips-card ul {
  margin: 0;
  padding-left: 20px;
}

.tips-card li {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

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

.nav-item.active {
  color: #667eea;
  font-weight: 700;
}

.nav-item span:first-child {
  font-size: 22px;
}
</style>