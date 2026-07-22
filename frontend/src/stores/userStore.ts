/**
 * 用户登录状态共享管理
 * 统一管理 token、user 基本信息的 localStorage 读写，提供响应式状态。
 */
import { ref, computed } from 'vue'
import { login as apiLogin, getProfile } from '../api/index'

// ── 状态 ──
const token = ref<string>(localStorage.getItem('token') || '')
const user = ref<Record<string, any> | null>(JSON.parse(localStorage.getItem('user') || 'null'))

const isLoggedIn = computed(() => !!token.value)

// ── 方法 ──

/** 从 localStorage 恢复状态 */
function load() {
  const t = localStorage.getItem('token')
  token.value = t || ''
  const u = localStorage.getItem('user')
  user.value = u ? JSON.parse(u) : null
}

/** 登录：调用 API，成功后存储 token + user */
async function login(phone: string, password: string) {
  const res = await apiLogin(phone, password)
  token.value = res.data.token
  user.value = res.data.user
  localStorage.setItem('token', res.data.token)
  localStorage.setItem('user', JSON.stringify(res.data.user))
  return res.data
}

/** 登出：清除状态和 localStorage */
function logout() {
  token.value = ''
  user.value = null
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

/** 直接设置 token 和 user（注册成功后使用） */
function setAuth(t: string, u: Record<string, any>) {
  token.value = t
  user.value = u
  localStorage.setItem('token', t)
  localStorage.setItem('user', JSON.stringify(u))
}

/** 从服务端拉取最新 profile 并更新 user */
async function fetchProfile() {
  const res = await getProfile()
  const data = res.data
  user.value = { ...user.value, ...data }
  localStorage.setItem('user', JSON.stringify(user.value))
  return data
}

/** 是否已实名认证 */
function hasRealName() {
  return !!(user.value?.real_name || user.value?.auth_status === 'approved')
}

export { token, user, isLoggedIn, load, login, logout, setAuth, fetchProfile, hasRealName }
