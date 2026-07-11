<template>
  <div class="rules-page">
    <header class="header" @click="router.back()">
      <span class="back-btn">← 返回</span>
      <h2>📋 打卡规则说明</h2>
      <span></span>
    </header>

    <div class="content">
      <section class="card">
        <h3>⏰ 挑战时间</h3>
        <p>活动周期为 <strong>连续21天</strong>，从你完成第1天打卡开始计算。每天可以打卡新一天的内容，无需连续日历日。</p>
        <div class="highlight-box">
          <span>📅</span>
          <span>建议每天完成当日任务，养成良好习惯！</span>
        </div>
      </section>

      <section class="card">
        <h3>✅ 打卡判定标准</h3>
        <ul class="check-list">
          <li><span class="dot green"></span>完成当日问卷所有必填项</li>
          <li><span class="dot green"></span>上网活动至少选择一项</li>
          <li><span class="dot green"></span>思考题回答不少于5个字</li>
          <li><span class="dot green"></span>填写上网带来的影响</li>
        </ul>
        <p class="note">以上条件全部满足，系统判定为有效打卡。</p>
      </section>

      <section class="card">
        <h3>❌ 无效打卡判定</h3>
        <ul class="check-list">
          <li><span class="dot red"></span>思考题回答少于5个字</li>
          <li><span class="dot red"></span>未填写上网影响</li>
          <li><span class="dot red"></span>重复打卡同一天</li>
          <li><span class="dot red"></span>跳过天数强行打卡</li>
        </ul>
      </section>

      <section class="card">
        <h3>🔄 补卡规则</h3>
        <div class="highlight-box yellow">
          <span>⚠️</span>
          <span>活动不支持补卡！每天只能按顺序逐天打卡，漏掉的天数无法补回。所以一定要坚持每天打卡哦～</span>
        </div>
      </section>

      <section class="card">
        <h3>🏅 勋章获取条件</h3>
        <div class="badge-list">
          <div class="badge-row"><span>🌱</span><span><strong>初次打卡</strong> — 完成第1天打卡</span></div>
          <div class="badge-row"><span>🔥</span><span><strong>三天坚持</strong> — 连续打卡3天</span></div>
          <div class="badge-row"><span>⭐</span><span><strong>一周达人</strong> — 连续打卡7天</span></div>
          <div class="badge-row"><span>🌟</span><span><strong>半月之星</strong> — 连续打卡14天</span></div>
          <div class="badge-row"><span>🏆</span><span><strong>21天满贯</strong> — 完成全部21天</span></div>
          <div class="badge-row"><span>💪</span><span><strong>过半勇士</strong> — 完成10天以上</span></div>
          <div class="badge-row"><span>📚</span><span><strong>学习达人</strong> — 学习占比超过40%</span></div>
          <div class="badge-row"><span>💚</span><span><strong>健康上网</strong> — 日均上网&lt;3小时</span></div>
          <div class="badge-row"><span>👑</span><span><strong>超级打卡王</strong> — 满21天连胜</span></div>
        </div>
      </section>

      <section class="card">
        <h3>📊 数据说明</h3>
        <ul class="check-list">
          <li><span class="dot blue"></span>上网时长分为4档：0-1h / 1-3h / 3-5h / 5h以上</li>
          <li><span class="dot blue"></span>&gt;3小时视为超标上网</li>
          <li><span class="dot blue"></span>打卡记录包含IP地址和设备信息，用于防止作弊</li>
          <li><span class="dot blue"></span>所有数据仅用于活动统计，保护个人隐私</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.rules-page {
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
  cursor: pointer;
}
.back-btn { color: #667eea; font-weight: 600; font-size: 14px; }
.header h2 { font-size: 17px; margin: 0; color: #333; }
.content { padding: 14px 16px; }
.card {
  background: white;
  border-radius: 16px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.card h3 { margin: 0 0 10px; font-size: 16px; color: #333; }
.card p { font-size: 14px; color: #555; line-height: 1.7; margin: 0; }
.card .note { font-size: 12px; color: #999; margin-top: 8px; }
.highlight-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #f0f4ff;
  border-radius: 10px;
  padding: 12px;
  margin-top: 10px;
  font-size: 13px;
  color: #555;
  line-height: 1.6;
}
.highlight-box.yellow { background: #fffbeb; }
.check-list { list-style: none; padding: 0; margin: 0; }
.check-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
  padding: 6px 0;
}
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot.green { background: #2ed573; }
.dot.red { background: #ff6b6b; }
.dot.blue { background: #667eea; }
.badge-list { display: flex; flex-direction: column; gap: 6px; }
.badge-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #555;
  padding: 4px 0;
}
.badge-row span:first-child { font-size: 20px; }
strong { color: #333; }
</style>
