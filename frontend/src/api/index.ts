import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：自动添加Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

export function sendCode(phone: string, purpose: string = 'register') {
  return api.post('/send-code/', { phone, purpose })
}

export function register(phone: string, code: string, password: string, nickname: string = '') {
  return api.post('/register/', { phone, code, password, nickname })
}

export function login(phone: string, password: string) {
  return api.post('/login/', { phone, password })
}

export function getProfile() {
  return api.get('/profile/')
}

export function updateProfile(data: Record<string, any>) {
  return api.put('/profile/', data)
}

export function getSchools() {
  return api.get('/schools/')
}

export function getAchievements() {
  return api.get('/achievements/')
}

export function getQuizQuestions(day: number) {
  return api.get('/quiz/questions/', { params: { day } })
}

export function submitQuiz(answers: Record<string, string>, day: number) {
  return api.post('/quiz/submit/', { answers, day })
}

export function getQuizHistory() {
  return api.get('/quiz/history/')
}

export function submitAuth(data: Record<string, any>) {
  return api.post('/auth/submit/', data)
}

export function getAuthReviewList(status?: string) {
  return api.get('/admin/auth-review/', { params: status ? { status } : {} })
}

export function reviewAuth(profileId: number, action: string, reason: string = '') {
  return api.post('/admin/auth-review/', { profile_id: profileId, action, reason })
}

export function getNotifications(page: number = 1, pageSize: number = 20) {
  return api.get('/notifications/', { params: { page, page_size: pageSize } })
}

export function markNotificationsRead(id: number) {
  return api.post('/notifications/', { id })
}

export function markAllNotificationsRead() {
  return api.post('/notifications/', {})
}

export function getTopics() {
  return api.get('/topics/')
}

export function getCheckIns() {
  return api.get('/checkin/')
}

export function submitCheckIn(data: Record<string, any>) {
  return api.post('/checkin/', data)
}

export function getCheckInStats() {
  return api.get('/checkin/stats/')
}

export function getUsageStats() {
  return api.get('/usage-stats/')
}

export function getMessages(page: number = 1, pageSize: number = 20) {
  return api.get('/messages/', { params: { page, page_size: pageSize } })
}

export function postMessage(content: string) {
  return api.post('/messages/', { content })
}

export function replyMessage(messageId: number, content: string) {
  return api.post(`/messages/${messageId}/reply/`, { content })
}

export function likeMessage(messageId: number) {
  return api.post(`/messages/${messageId}/like/`)
}

export default api
