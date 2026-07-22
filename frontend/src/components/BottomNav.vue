<template>
  <nav class="bottom-nav">
    <button
      v-for="tab in tabs"
      :key="tab.key"
      class="nav-item"
      :class="{ active: activeTab === tab.key }"
      @click="navigate(tab)"
    >
      <span>{{ tab.icon }}</span>
      <span>{{ tab.label }}</span>
    </button>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { isLoggedIn } from '../stores/userStore'

const props = defineProps({
  activeTab: { type: String, default: '' },
})

const router = useRouter()

const tabs = [
  { key: 'home',     icon: '🏠', label: '首页', path: '/' },
  { key: 'checkin',  icon: '📅', label: '打卡', path: '/checkin' },
  { key: 'stats',    icon: '📊', label: '统计', path: '/stats' },
  { key: 'messages', icon: '💬', label: '留言', path: '/messages' },
  { key: 'my',       icon: '👤', label: '我的', path: '/my' },
]

function navigate(tab) {
  // 打卡、统计、留言页面需要先登录
  const requiresAuth = ['checkin', 'stats', 'messages']
  if (requiresAuth.includes(tab.key) && !isLoggedIn.value) {
    router.push('/login')
    return
  }
  router.push(tab.path)
}
</script>

<style>
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
.nav-item.active { color: var(--color-primary); font-weight: 700; }
.nav-item span:first-child { font-size: 22px; }
</style>
