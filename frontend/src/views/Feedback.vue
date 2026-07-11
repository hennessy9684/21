<template>
  <div class="feedback-page">
    <header class="header" @click="router.back()">
      <span class="back-btn">← 返回</span>
      <h2>💬 反馈与帮助</h2>
      <span></span>
    </header>

    <div class="content">
      <!-- 常见问题 -->
      <section class="card">
        <h3>🙋 常见问题</h3>
        <div v-for="faq in faqs" :key="faq.q" class="faq-item" @click="faq.open = !faq.open">
          <div class="faq-q">
            <span>{{ faq.q }}</span>
            <span class="faq-arrow" :class="{ open: faq.open }">▼</span>
          </div>
          <p v-if="faq.open" class="faq-a">{{ faq.a }}</p>
        </div>
      </section>

      <!-- 提交反馈 -->
      <section class="card">
        <h3>📝 提交反馈</h3>
        <div class="field">
          <label>问题类型</label>
          <select v-model="form.type">
            <option value="bug">打卡Bug</option>
            <option value="rule">规则疑惑</option>
            <option value="suggest">功能建议</option>
            <option value="other">其他问题</option>
          </select>
        </div>
        <div class="field">
          <label>问题描述</label>
          <textarea v-model="form.content" placeholder="详细描述你遇到的问题..." rows="4"></textarea>
        </div>
        <div class="field">
          <label>联系方式（选填）</label>
          <input v-model="form.contact" placeholder="手机号或微信，方便我们联系你" />
        </div>
        <button class="btn-submit" @click="submitFeedback" :disabled="!form.content.trim() || submitting">
          {{ submitting ? '提交中...' : '提交反馈' }}
        </button>
        <p v-if="msg" class="msg" :class="{ ok: msgOk }">{{ msg }}</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { postMessage } from '../api/index.js'

const router = useRouter()
const submitting = ref(false)
const msg = ref('')
const msgOk = ref(false)

const faqs = reactive([
  { q: '忘记打卡了怎么办？', a: '活动不支持补卡，每天只能按顺序逐天打卡。建议设置每日提醒，养成定时打卡的习惯。', open: false },
  { q: '打卡提交后可以修改吗？', a: '打卡一旦提交后无法修改，请认真填写每一份问卷。', open: false },
  { q: '徽章什么时候会更新？', a: '完成对应条件后，徽章会立即解锁。你可以在「我的」→「成就徽章」中查看。', open: false },
  { q: '连续打卡天数怎么算？', a: '连续打卡天数是从你最近打卡天往前数连续的天数，中间不能有断档。', open: false },
  { q: '上网时长选错了有影响吗？', a: '时长数据用于统计报告，不会影响打卡判定。建议如实填写。', open: false },
])

const form = reactive({ type: 'bug', content: '', contact: '' })

async function submitFeedback() {
  submitting.value = true
  msg.value = ''
  try {
    const content = `[${form.type === 'bug' ? 'Bug反馈' : form.type === 'rule' ? '规则疑惑' : form.type === 'suggest' ? '功能建议' : '其他'}] ${form.content}` + (form.contact ? ` (联系方式: ${form.contact})` : '')
    await postMessage(content)
    msgOk.value = true
    msg.value = '感谢反馈！我们会尽快处理。'
    form.content = ''
    form.contact = ''
  } catch (e) {
    msgOk.value = false
    msg.value = '提交失败，请稍后重试'
  }
  submitting.value = false
  setTimeout(() => { msg.value = '' }, 3000)
}
</script>

<style scoped>
.feedback-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4ff, #fdf2f8, #f0fdf4);
  padding-bottom: 30px;
  font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; background: white;
  position: sticky; top: 0; z-index: 30; cursor: pointer;
}
.back-btn { color: #667eea; font-weight: 600; font-size: 14px; }
.header h2 { font-size: 17px; margin: 0; color: #333; }
.content { padding: 14px 16px; }
.card {
  background: white; border-radius: 16px; padding: 18px;
  margin-bottom: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.card h3 { margin: 0 0 12px; font-size: 16px; color: #333; }

.faq-item { border-bottom: 1px solid #f5f5f5; padding: 10px 0; cursor: pointer; }
.faq-item:last-child { border-bottom: none; }
.faq-q { display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 600; color: #444; }
.faq-arrow { font-size: 10px; color: #ccc; transition: transform 0.2s; }
.faq-arrow.open { transform: rotate(180deg); color: #667eea; }
.faq-a { font-size: 13px; color: #888; line-height: 1.6; margin: 8px 0 0; padding-left: 0; }

.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; font-weight: 600; color: #666; margin-bottom: 6px; }
.field select, .field input, .field textarea {
  width: 100%; border: 2px solid #e8ecf4; border-radius: 12px;
  padding: 10px 14px; font-size: 14px; outline: none;
  box-sizing: border-box; font-family: inherit;
  background: #fafbfd; transition: border-color 0.2s;
}
.field select:focus, .field input:focus, .field textarea:focus { border-color: #667eea; }
.field textarea { resize: none; }
.btn-submit {
  width: 100%; background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; border: none; padding: 14px; border-radius: 14px;
  font-size: 15px; font-weight: 700; cursor: pointer;
}
.btn-submit:disabled { opacity: 0.5; }
.msg { text-align: center; font-size: 13px; margin-top: 8px; color: #ff4757; }
.msg.ok { color: #2ed573; }
</style>
