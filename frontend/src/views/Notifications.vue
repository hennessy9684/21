<template>
  <div class="notif-page">
    <header class="header">
      <button class="back-btn" @click="router.back()">← 返回</button>
      <h2>🔔 消息通知</h2>
      <button class="mark-btn" @click="markAll" v-if="unreadCount > 0">全部已读</button>
    </header>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="notifs.length === 0" class="empty">
      <span>🔕</span>
      <h3>暂无通知</h3>
      <p>完成打卡、获得勋章后这里会有通知</p>
    </div>

    <div v-else class="notif-list">
      <div v-for="n in notifs" :key="n.id" class="notif-card" :class="{ unread: !n.is_read }" @click="readNotif(n)">
        <div class="n-icon">
          <template v-if="n.n_type === 'badge'">🏅</template>
          <template v-else-if="n.n_type === 'reminder'">🔔</template>
          <template v-else-if="n.n_type === 'bug_fix'">🛠️</template>
          <template v-else>📢</template>
        </div>
        <div class="n-body">
          <div class="n-header">
            <span class="n-title">{{ n.title }}</span>
            <span v-if="!n.is_read" class="n-dot"></span>
          </div>
          <p class="n-content">{{ n.content }}</p>
          <span class="n-time">{{ formatTime(n.created_at, 'short') }}</span>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore" class="load-more-wrap">
      <button class="btn-load-more" @click="loadMore" :disabled="loadingMore">
        {{ loadingMore ? '加载中...' : '加载更多 ▼' }}
      </button>
    </div>
    <div v-else-if="notifs.length > 0" class="load-more-wrap">
      <span class="no-more">— 已显示全部通知 —</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getNotifications, markNotificationsRead, markAllNotificationsRead } from '../api/index'
import { formatTime } from '../utils/time'

const router = useRouter()
const notifs = ref([])
const unreadCount = ref(0)
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const hasMore = ref(false)

async function loadNotifs(reset = true) {
  if (reset) {
    page.value = 1
    loading.value = true
  }
  try {
    const res = await getNotifications(page.value)
    const data = res.data
    const items = data.results || []
    if (reset) {
      notifs.value = items
    } else {
      notifs.value.push(...items)
    }
    unreadCount.value = data.unread_count || 0
    hasMore.value = data.has_more
  } catch (e) { console.error(e) }
  loading.value = false
  loadingMore.value = false
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  page.value++
  await loadNotifs(false)
}

async function readNotif(n) {
  if (n.is_read) return
  try {
    await markNotificationsRead(n.id)
    n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (e) { console.error(e) }
}

async function markAll() {
  try {
    await markAllNotificationsRead()
    notifs.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
  } catch (e) { console.error(e) }
}

onMounted(loadNotifs)
</script>

<style scoped>
.notif-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4ff, #fdf2f8, #f0fdf4);
  padding-bottom: 30px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: white;
  position: sticky;
  top: 0;
  z-index: 30;
}
.back-btn {
  background: none; border: none; color: var(--color-accent);
  font-weight: 600; font-size: 14px; cursor: pointer;
}
.header h2 { font-size: 17px; margin: 0; color: #333; }
.mark-btn {
  background: none; border: none; color: var(--color-accent);
  font-size: 13px; cursor: pointer; font-weight: 600;
}

.loading { text-align: center; padding: 60px; color: #888; }
.empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 80px 20px; text-align: center;
}
.empty span { font-size: 56px; margin-bottom: 12px; }
.empty h3 { margin: 0 0 6px; color: #333; }
.empty p { color: #888; font-size: 14px; }

.notif-list { padding: 8px 16px; }
.notif-card {
  background: white;
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 10px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
  transition: transform 0.15s;
}
.notif-card:active { transform: scale(0.98); }
.notif-card.unread { border-left: 3px solid var(--color-accent); background: #fafbff; }
.n-icon { font-size: 28px; flex-shrink: 0; }
.n-body { flex: 1; min-width: 0; }
.n-header { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.n-title { font-size: 14px; font-weight: 700; color: #333; }
.n-dot { width: 7px; height: 7px; background: var(--color-danger); border-radius: 50%; }
.n-content { font-size: 13px; color: #666; margin: 0 0 6px; line-height: 1.5; }
.n-time { font-size: 11px; color: #bbb; }

/* Load More */
.load-more-wrap {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}
.btn-load-more {
  background: white;
  border: 2px solid #e8ecf4;
  color: var(--color-accent);
  padding: 10px 32px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-load-more:hover:not(:disabled) {
  background: #f0f4ff;
  border-color: var(--color-accent);
}
.btn-load-more:disabled { opacity: 0.5; cursor: default; }
.no-more {
  font-size: 12px;
  color: #bbb;
}
</style>
