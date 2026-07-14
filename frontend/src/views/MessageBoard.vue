<template>
  <div class="msg-page">
    <!-- Header -->
    <header class="header">
      <span class="header-icon">💬</span>
      <h2>留言板</h2>
      <span class="header-count">{{ messages.length }}条留言</span>
    </header>

    <!-- 发布留言 -->
    <div class="post-area">
      <div class="post-header">
        <span class="post-avatar">🧒</span>
        <span class="post-name">{{ userName }}</span>
      </div>
      <textarea v-model="newContent" class="post-input" placeholder="有什么想说的？写下你的想法、疑惑或打卡心得..." rows="3"></textarea>
      <div class="post-footer">
        <span class="post-hint">{{ newContent.length }}/200</span>
        <button class="btn-post" @click="postMsg" :disabled="!newContent.trim() || posting">
          {{ posting ? '发送中...' : '发布留言 ✨' }}
        </button>
      </div>
      <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
    </div>

    <!-- 留言列表 -->
    <div class="msg-list">
      <div v-if="loading" class="loading-state">
        <span>📬</span><p>加载中...</p>
      </div>

      <div v-else-if="messages.length === 0" class="empty-state">
        <span class="empty-icon">�</span>
        <h3>还没有留言</h3>
        <p>快来写下第一条留言吧～</p>
      </div>

      <div v-for="msg in messages" :key="msg.id" class="msg-card">
        <!-- 留言主体 -->
        <div class="msg-header">
          <span class="msg-avatar">{{ getAvatar(msg.nickname) }}</span>
          <div class="msg-user">
            <span class="msg-name">{{ msg.nickname || msg.username }}</span>
            <span class="msg-time">{{ formatTime(msg.created_at) }}</span>
          </div>
        </div>
        <p class="msg-content">{{ msg.content }}</p>

        <!-- 操作栏 -->
        <div class="msg-actions">
          <button class="action-btn" :class="{ liked: msg.is_liked }" @click="toggleLike(msg)">
            <span>{{ msg.is_liked ? '❤️' : '�' }}</span>
            <span>{{ msg.like_count || 0 }}</span>
          </button>
          <button class="action-btn" @click="toggleReply(msg)">
            <span>💬</span>
            <span>{{ msg.reply_count || msg.replies?.length || 0 }}</span>
          </button>
        </div>

        <!-- 回复区域 -->
        <div v-if="msg.showReply" class="reply-section">
          <!-- 已有回复 -->
          <div v-for="reply in msg.replies" :key="reply.id" class="reply-item">
            <span class="reply-avatar">{{ getAvatar(reply.nickname) }}</span>
            <div class="reply-body">
              <div class="reply-header">
                <span class="reply-name">{{ reply.nickname || reply.username }}</span>
                <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
              </div>
              <p class="reply-text">{{ reply.content }}</p>
            </div>
          </div>

          <!-- 回复输入框 -->
          <div class="reply-input-row">
            <input v-model="msg.replyText" class="reply-input" placeholder="写下回复..." @keyup.enter="sendReply(msg)" />
            <button class="btn-send-reply" @click="sendReply(msg)" :disabled="!msg.replyText?.trim()">发送</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
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
      <button class="nav-item active">
        <span>💬</span><span>留言</span>
      </button>
      <button class="nav-item" @click="router.push('/my')">
        <span>👤</span><span>我的</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getMessages, postMessage, replyMessage, likeMessage } from '../api/index.js'

const router = useRouter()
const messages = ref([])
const newContent = ref('')
const posting = ref(false)
const errorMsg = ref('')
const loading = ref(true)

const user = JSON.parse(localStorage.getItem('user') || '{}')
const userName = computed(() => user.nickname || '小朋友')

const avatars = ['🦊', '🐱', '🐶', '🐼', '🐨', '🐰', '🦁', '🐸', '🐵', '🐯', '🐮', '🐷']

function getAvatar(name) {
  if (!name) return '🧒'
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return avatars[Math.abs(hash) % avatars.length]
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  const pad = n => n.toString().padStart(2, '0')
  return `${d.getMonth() + 1}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

async function loadMessages() {
  try {
    const res = await getMessages()
    messages.value = res.data.map(m => ({
      ...m,
      showReply: false,
      replyText: '',
    }))
  } catch (e) {
    console.error(e)
  }
  loading.value = false
}

async function postMsg() {
  const content = newContent.value.trim()
  if (!content || content.length > 200) return
  posting.value = true
  errorMsg.value = ''
  try {
    const res = await postMessage(content)
    messages.value.unshift({ ...res.data, showReply: false, replyText: '', replies: [] })
    newContent.value = ''
  } catch (e) {
    errorMsg.value = e.response?.data?.error || '发布失败，请稍后重试'
  }
  posting.value = false
}

async function toggleLike(msg) {
  try {
    const res = await likeMessage(msg.id)
    msg.is_liked = res.data.liked
    msg.like_count = res.data.like_count
  } catch (e) {
    console.error(e)
  }
}

function toggleReply(msg) {
  msg.showReply = !msg.showReply
}

async function sendReply(msg) {
  const content = (msg.replyText || '').trim()
  if (!content) return
  try {
    const res = await replyMessage(msg.id, content)
    if (!msg.replies) msg.replies = []
    msg.replies.push(res.data)
    msg.reply_count = (msg.reply_count || 0) + 1
    msg.replyText = ''
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadMessages)
</script>

<style scoped>
.msg-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #87CEEB 0%, #E0F4FF 40%, #F0FDF4 100%);
  padding-bottom: 80px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(12px);
}
.header-icon { font-size: 28px; }
.header h2 { margin: 0; font-size: 18px; font-weight: 800; color: #333; flex: 1; }
.header-count { font-size: 13px; color: #999; }

/* Post */
.post-area {
  background: white;
  border-radius: 20px;
  margin: 8px 16px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.post-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.post-avatar { font-size: 24px; }
.post-name { font-size: 14px; font-weight: 700; color: #333; }
.post-input {
  width: 100%;
  border: 2px solid #f0e6d6;
  border-radius: 14px;
  padding: 12px;
  font-size: 14px;
  resize: none;
  outline: none;
  box-sizing: border-box;
  font-family: inherit;
  background: #fffbeb;
  transition: border-color 0.2s;
}
.post-input:focus { border-color: #f9ca24; }
.post-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
}
.post-hint { font-size: 12px; color: #aaa; }
.btn-post {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s;
}
.btn-post:hover:not(:disabled) { transform: scale(1.04); }
.btn-post:disabled { opacity: 0.5; }
.error-text { color: #ff4757; font-size: 12px; margin: 8px 0 0; text-align: center; }

/* Message List */
.msg-list { padding: 8px 16px; }
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}
.loading-state span { font-size: 48px; }
.loading-state p { color: #888; }
.empty-icon { font-size: 56px; margin-bottom: 12px; }
.empty-state h3 { color: #333; margin: 0 0 6px; font-size: 16px; }
.empty-state p { color: #888; font-size: 14px; }

/* Message Card */
.msg-card {
  background: white;
  border-radius: 20px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.msg-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.msg-avatar { font-size: 32px; }
.msg-user { display: flex; flex-direction: column; gap: 2px; }
.msg-name { font-size: 14px; font-weight: 700; color: #333; }
.msg-time { font-size: 11px; color: #aaa; }
.msg-content {
  font-size: 15px;
  color: #444;
  line-height: 1.6;
  margin: 0 0 12px;
  word-break: break-word;
}

/* Actions */
.msg-actions {
  display: flex;
  gap: 16px;
  border-top: 1px solid #f5f5f5;
  padding-top: 10px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  font-size: 13px;
  color: #888;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 10px;
  transition: all 0.2s;
}
.action-btn:hover { background: #f5f5f5; }
.action-btn.liked { color: #ff6b6b; }

/* Reply Section */
.reply-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #f0e6d6;
}
.reply-item {
  display: flex;
  gap: 8px;
  padding: 8px 0;
}
.reply-item + .reply-item { border-top: 1px solid #fafafa; }
.reply-avatar { font-size: 24px; flex-shrink: 0; }
.reply-body { flex: 1; min-width: 0; }
.reply-header { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.reply-name { font-size: 13px; font-weight: 600; color: #3b82f6; }
.reply-time { font-size: 11px; color: #bbb; }
.reply-text { font-size: 13px; color: #555; margin: 0; line-height: 1.5; }
.reply-input-row {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.reply-input {
  flex: 1;
  border: 2px solid #e8ecf4;
  border-radius: 20px;
  padding: 8px 14px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}
.reply-input:focus { border-color: #3b82f6; }
.btn-send-reply {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}
.btn-send-reply:disabled { opacity: 0.5; }

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
  padding: 5px 16px;
}
.nav-item.active { color: #3b82f6; font-weight: 700; }
.nav-item span:first-child { font-size: 22px; }
</style>
