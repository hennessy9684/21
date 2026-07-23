<template>
  <div class="login-page">
    <div class="login-container">
      <div class="mascot">🦊</div>
      <h1 class="title">21天安全用网打卡</h1>
      <p class="subtitle">和小伙伴一起，成为网络安全小达人！</p>

      <!-- Tab -->
      <div class="tab-bar">
        <span :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</span>
        <span :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</span>
      </div>

      <!-- Login Form -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="form">
        <div class="input-group">
          <span class="input-icon">📱</span>
          <input v-model="loginForm.phone" type="tel" maxlength="11" placeholder="请输入手机号" required>
        </div>
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input v-model="loginForm.password" type="password" placeholder="请输入密码" required>
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
        <p v-if="loginError" class="error">{{ loginError }}</p>
      </form>

      <!-- Register Form -->
      <form v-else @submit.prevent="handleRegister" class="form">
        <div class="input-group">
          <span class="input-icon">📱</span>
          <input v-model="regForm.phone" type="tel" maxlength="11" placeholder="请输入手机号" required>
        </div>
        <div class="input-group code-group">
          <span class="input-icon">✉️</span>
          <input v-model="regForm.code" type="text" maxlength="6" placeholder="验证码" required>
          <button type="button" class="btn-code" @click="handleSendCode" :disabled="codeSending || countdown > 0">
            {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
          </button>
        </div>
        <div class="input-group">
          <span class="input-icon">🔑</span>
          <input v-model="regForm.password" type="password" placeholder="设置密码（6位以上）" required>
        </div>
        <div class="input-group">
          <span class="input-icon">😊</span>
          <input v-model="regForm.nickname" type="text" placeholder="昵称（选填）">
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? '注册中...' : '注 册' }}
        </button>
        <p v-if="regError" class="error">{{ regError }}</p>
      </form>

      <p v-if="success" class="success">{{ success }}</p>

      <div class="admin-link mt-20">
        <span class="divider-text">—</span>
        <button class="btn-admin" @click="goToAdminLogin">
          <span>⚙️</span> 管理员登录
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { sendCode, register } from '../api/index'
import { login as userStoreLogin, setAuth } from '../stores/userStore'

const router = useRouter()
const mode = ref('login')
const loading = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const loginError = ref('')
const regError = ref('')
const success = ref('')

const loginForm = reactive({ phone: '', password: '' })
const regForm = reactive({ phone: '', code: '', password: '', nickname: '' })

function goToAdminLogin() {
  window.location.href = '/manage/signin/'
}

async function handleSendCode() {
  if (!/^1\d{10}$/.test(regForm.phone)) {
    regError.value = '请输入正确的手机号'
    return
  }
  regError.value = ''
  codeSending.value = true
  try {
    const res = await sendCode(regForm.phone, 'register')
    success.value = res.data.message || '验证码已发送，请查看手机短信'
    startCountdown()
  } catch (e) {
    regError.value = e.response?.data?.error || '发送失败，请重试'
  }
  codeSending.value = false
}

function startCountdown() {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) clearInterval(timer)
  }, 1000)
}

async function handleLogin() {
  loading.value = true
  loginError.value = ''
  try {
    console.log('Login attempt:', loginForm.phone, loginForm.password)
    const data = await userStoreLogin(loginForm.phone, loginForm.password)
    console.log('Login response:', data)
    
    const role = data.user.role || 'user'
    if (role === 'admin' || role === 'super_admin') {
      window.location.href = '/manage/signin/'
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error('Login error:', e)
    console.error('Response:', e.response?.status, e.response?.data)
    const msg = e.response?.data?.error || e.response?.data?.detail || e.response?.data?.phone || '登录失败，请检查账号密码'
    loginError.value = typeof msg === 'string' ? msg : JSON.stringify(msg)
  }
  loading.value = false
}

async function handleRegister() {
  if (!/^1\d{10}$/.test(regForm.phone)) {
    regError.value = '请输入正确的手机号'
    return
  }
  if (regForm.password.length < 6) {
    regError.value = '密码至少6位'
    return
  }
  if (!regForm.code) {
    regError.value = '请输入验证码'
    return
  }
  loading.value = true
  regError.value = ''
  try {
        const res = await register(regForm.phone, regForm.code, regForm.password, regForm.nickname)
        setAuth(res.data.token, res.data.user)
        router.push('/my')  // 注册后先完善个人信息
  } catch (e) {
    regError.value = e.response?.data?.error || '注册失败'
  }
  loading.value = false
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.login-container {
  background: white;
  border-radius: 30px;
  padding: 40px 30px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  text-align: center;
  position: relative;
  overflow: hidden;
}
.mascot {
  font-size: 80px;
  margin-bottom: 10px;
  animation: bounce 2s infinite;
}
@keyframes bounce {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
.title {
  font-size: 24px;
  color: #333;
  margin: 0 0 5px;
  font-weight: 800;
}
.subtitle {
  color: #888;
  font-size: 14px;
  margin: 0 0 25px;
}
.tab-bar {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 25px;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}
.tab-bar span {
  font-size: 16px;
  color: #999;
  cursor: pointer;
  padding: 0 5px 10px;
  position: relative;
  font-weight: 600;
  transition: color 0.3s;
}
.tab-bar span.active {
  color: var(--color-accent);
}
.tab-bar span.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--color-accent);
  border-radius: 3px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.input-group {
  display: flex;
  align-items: center;
  background: #f5f7fb;
  border-radius: 15px;
  padding: 0 15px;
  border: 2px solid transparent;
  transition: border-color 0.3s;
}
.input-group:focus-within {
  border-color: var(--color-accent);
}
.input-icon {
  font-size: 20px;
  margin-right: 10px;
}
.input-group input {
  flex: 1;
  border: none;
  background: none;
  padding: 14px 0;
  font-size: 15px;
  outline: none;
  color: #333;
}
.code-group .btn-code {
  white-space: nowrap;
  background: var(--color-accent);
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  font-weight: 600;
}
.code-group .btn-code:disabled {
  background: #ccc;
}
.btn-primary {
  background: var(--gradient-accent);
  color: white;
  border: none;
  padding: 15px;
  border-radius: 15px;
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 5px;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102,126,234,0.4);
}
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: var(--color-danger);
  font-size: 13px;
  margin: 0;
}
.success {
  color: var(--color-success);
  font-size: 13px;
  margin: 10px 0 0;
}

.admin-link {
  padding-top: 14px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-admin {
  font-size: 13px;
  color: #aaa;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color 0.3s;
}
.btn-admin:hover {
  color: var(--color-accent);
}
.btn-admin span {
  font-size: 14px;
}


</style>
