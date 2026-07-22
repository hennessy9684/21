import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import CheckIn from '../views/CheckIn.vue'
import MessageBoard from '../views/MessageBoard.vue'
import Stats from '../views/Stats.vue'
import My from '../views/My.vue'
import Rules from '../views/Rules.vue'
import Notifications from '../views/Notifications.vue'
import Feedback from '../views/Feedback.vue'
import Privacy from '../views/Privacy.vue'
import QuizHistory from '../views/QuizHistory.vue'
import RealNameAuth from '../views/RealNameAuth.vue'
import { token } from '../stores/userStore'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/checkin', name: 'CheckIn', component: CheckIn, meta: { requiresAuth: true } },
  { path: '/messages', name: 'Messages', component: MessageBoard, meta: { requiresAuth: true } },
  { path: '/stats', name: 'Stats', component: Stats, meta: { requiresAuth: true } },
  { path: '/my', name: 'My', component: My, meta: { requiresAuth: true } },
  { path: '/rules', name: 'Rules', component: Rules },
  { path: '/notifications', name: 'Notifications', component: Notifications, meta: { requiresAuth: true } },
  { path: '/feedback', name: 'Feedback', component: Feedback, meta: { requiresAuth: true } },
  { path: '/privacy', name: 'Privacy', component: Privacy, meta: { requiresAuth: true } },
  { path: '/quiz-history', name: 'QuizHistory', component: QuizHistory, meta: { requiresAuth: true } },
  { path: '/auth', name: 'RealNameAuth', component: RealNameAuth, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !token.value) {
    next('/login')
  } else {
    next()
  }
})

export default router
