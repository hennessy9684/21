<template>
  <div class="privacy-page">
    <header class="header" @click="router.back()">
      <span class="back-btn">← 返回</span>
      <h2>🔐 隐私设置</h2>
      <span></span>
    </header>

    <div class="content">
      <section class="card">
        <h3>👁️ 个人信息可见性</h3>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">公开打卡进度</span>
            <span class="sr-desc">在留言板排行榜中展示你的打卡天数和进度</span>
          </div>
          <label class="toggle"><input type="checkbox" v-model="settings.showRecords" @change="save" /><span class="slider"></span></label>
        </div>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">公开昵称</span>
            <span class="sr-desc">在留言和排行榜中显示你的昵称</span>
          </div>
          <label class="toggle"><input type="checkbox" v-model="settings.showNickname" @change="save" /><span class="slider"></span></label>
        </div>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">公开统计数据</span>
            <span class="sr-desc">允许其他用户查看你的上网时长统计</span>
          </div>
          <label class="toggle"><input type="checkbox" v-model="settings.showStats" @change="save" /><span class="slider"></span></label>
        </div>
      </section>

      <section class="card">
        <h3>🔔 通知偏好</h3>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">打卡提醒通知</span>
            <span class="sr-desc">每天18:00发送打卡提醒</span>
          </div>
          <label class="toggle"><input type="checkbox" v-model="settings.reminder" @change="save" /><span class="slider"></span></label>
        </div>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">勋章达成通知</span>
            <span class="sr-desc">获得新勋章时发送通知</span>
          </div>
          <label class="toggle"><input type="checkbox" v-model="settings.badgeNotify" @change="save" /><span class="slider"></span></label>
        </div>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">活动通知</span>
            <span class="sr-desc">接收官方活动公告和新功能通知</span>
          </div>
          <label class="toggle"><input type="checkbox" v-model="settings.eventNotify" @change="save" /><span class="slider"></span></label>
        </div>
      </section>

      <section class="card">
        <h3>📊 数据管理</h3>
        <div class="setting-row">
          <div class="sr-left">
            <span class="sr-title">数据收集说明</span>
            <span class="sr-desc">我们收集的上网数据仅用于生成个人报告和活动统计，不会分享给第三方。打卡时采集的IP地址和设备信息仅用于身份验证和防作弊。</span>
          </div>
        </div>
        <p class="privacy-note">如需删除全部数据，请联系管理员: 751200983@qq.com</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const settings = reactive({
  showRecords: true,
  showNickname: true,
  showStats: false,
  reminder: true,
  badgeNotify: true,
  eventNotify: true,
})

function save() {
  localStorage.setItem('user_settings', JSON.stringify(settings))
}

onMounted(() => {
  const saved = localStorage.getItem('user_settings')
  if (saved) Object.assign(settings, JSON.parse(saved))
})
</script>

<style scoped>
.privacy-page {
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
.back-btn { color: var(--color-accent); font-weight: 600; font-size: 14px; }
.header h2 { font-size: 17px; margin: 0; color: #333; }
.content { padding: 14px 16px; }
.card {
  background: white; border-radius: 16px; padding: 18px;
  margin-bottom: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.card h3 { margin: 0 0 12px; font-size: 16px; color: #333; }

.setting-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 0; gap: 12px;
}
.setting-row + .setting-row { border-top: 1px solid #f5f5f5; }
.sr-left { display: flex; flex-direction: column; gap: 2px; }
.sr-title { font-size: 14px; font-weight: 600; color: #333; }
.sr-desc { font-size: 11px; color: #bbb; line-height: 1.4; }

.toggle { position: relative; width: 48px; height: 28px; flex-shrink: 0; }
.toggle input { display: none; }
.slider {
  position: absolute; inset: 0; background: #ddd; border-radius: 14px;
  cursor: pointer; transition: 0.3s;
}
.slider::after {
  content: ''; position: absolute; top: 3px; left: 3px;
  width: 22px; height: 22px; background: white;
  border-radius: 50%; transition: 0.3s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.toggle input:checked + .slider { background: var(--color-accent); }
.toggle input:checked + .slider::after { left: 23px; }

.privacy-note { font-size: 12px; color: #aaa; margin-top: 10px; text-align: center; }
</style>
