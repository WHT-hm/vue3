<template>
  <div class="exam-container" v-if="loaded">
    <div class="exam-header">
      <h2>{{ exam.name }}</h2>
      <div class="timer" :class="{ 'timer-warning': remainingMinutes < 5 }">
        剩余时间：{{ formatCountdown }}
      </div>
    </div>
    <div class="exam-body">
      <div v-for="(q, idx) in questions" :key="q.id" class="question-item">
        <el-card shadow="never">
          <div class="question-header">
            <el-tag size="small">{{ typeLabel(q.question_type) }}</el-tag>
            <span class="question-score">{{ q.score }} 分</span>
          </div>
          <div class="question-content">
            <span class="question-num">{{ idx + 1 }}.</span> {{ q.content }}
          </div>

          <!-- 选择题 -->
          <div v-if="q.question_type === 'choice'" class="question-options">
            <el-radio-group v-model="answers[q.id]" class="choice-radio-group" :class="getOptionLayout(q.options)">
              <el-radio
                v-for="opt in parseOptions(q.options)"
                :key="opt.label"
                :value="opt.label"
                class="choice-radio-item"
              >
                <div class="choice-option" :class="{ 'choice-option-active': answers[q.id] === opt.label }">
                  <span class="choice-circle">{{ opt.label }}</span>
                  <span class="choice-text">{{ opt.text }}</span>
                </div>
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 判断题 -->
          <div v-else-if="q.question_type === 'true_false'" class="question-options">
            <el-radio-group v-model="answers[q.id]" class="choice-radio-group layout-short">
              <el-radio value="对" class="choice-radio-item">
                <div class="choice-option" :class="{ 'choice-option-active': answers[q.id] === '对' }">
                  <span class="choice-circle">✓</span>
                  <span class="choice-text">对</span>
                </div>
              </el-radio>
              <el-radio value="错" class="choice-radio-item">
                <div class="choice-option" :class="{ 'choice-option-active': answers[q.id] === '错' }">
                  <span class="choice-circle">✗</span>
                  <span class="choice-text">错</span>
                </div>
              </el-radio>
            </el-radio-group>
          </div>

          <!-- 填空题 -->
          <div v-else-if="q.question_type === 'fill_blank'" class="question-options">
            <el-input v-model="answers[q.id]" placeholder="请输入答案" />
          </div>

          <!-- 简答题 -->
          <div v-else-if="q.question_type === 'short_answer'" class="question-options">
            <el-input v-model="answers[q.id]" type="textarea" :rows="3" placeholder="请输入答案" />
          </div>

          <!-- 编程题 -->
          <div v-else-if="q.question_type === 'programming'" class="question-options">
            <div class="programming-lang-hint">
              <el-tag :type="getLangTagType(q.language)" size="small" effect="dark">
                {{ getLangLabel(q.language) }}
              </el-tag>
              <span class="lang-hint-text">请使用 {{ getLangLabel(q.language) }} 编写代码</span>
            </div>
            <div class="code-editor-wrapper" :data-qid="q.id">
              <div class="line-numbers">
                <div v-for="n in getLineCount(answers[q.id])" :key="n" class="line-number">{{ n }}</div>
              </div>
              <textarea
                v-model="answers[q.id]"
                class="code-textarea"
                :placeholder="getCodePlaceholder(q.language)"
                spellcheck="false"
                @scroll="syncScroll(q.id)"
              ></textarea>
            </div>
            <div class="code-actions">
              <el-button type="success" size="small" @click="handleRunCode(q)" :loading="codeRunning[q.id]">
                运行测试
              </el-button>
            </div>
            <div v-if="codeResults[q.id]" class="code-result-panel">
              <div class="code-result-header">
                <span>运行结果</span>
                <el-tag :type="codeResults[q.id].correct ? 'success' : 'danger'" size="small">
                  {{ codeResults[q.id].correct ? '编译正确 ✓' : '编译错误 ✗' }}
                </el-tag>
              </div>
              <div class="code-result-body">
                <div class="code-output">
                  <strong>程序输出：</strong>
                  <pre>{{ codeResults[q.id].output || '（无输出）' }}</pre>
                </div>
                <div v-if="codeResults[q.id].error" class="code-error">
                  <strong>错误信息：</strong>
                  <pre>{{ codeResults[q.id].error }}</pre>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
    <div class="exam-footer">
      <el-button size="large" @click="handleBack">
        返回
      </el-button>
      <el-button type="primary" size="large" @click="handleSubmit" :loading="submitting">
        提交答案
      </el-button>
    </div>
  </div>
  <div v-else class="loading-container">
    <el-icon class="is-loading" :size="40"><Loading /></el-icon>
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { getExamQuestions, submitExam, runCode, checkExamStatus } from '../api/student'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const examId = computed(() => Number(route.params.id))

const loaded = ref(false)
const exam = ref({})
const questions = ref([])
const answers = ref({})
const submitting = ref(false)
const examStarted = ref(false)
const examForceEnded = ref(false) // 管理端强制结束标志

// 代码测试相关
const codeRunning = reactive({})
const codeResults = reactive({})

// 语言名称映射
const langMap = {
  python: 'Python',
  java: 'Java',
  c: 'C 语言',
  cpp: 'C++',
  'c++': 'C++',
}

// 获取语言显示名称
function getLangLabel(lang) {
  return langMap[lang] || lang || 'Python'
}

// 获取语言标签颜色
function getLangTagType(lang) {
  const typeMap = { python: 'success', java: 'danger', c: 'warning', cpp: '', 'c++': '' }
  return typeMap[lang] || 'success'
}

// 获取代码占位符
function getCodePlaceholder(lang) {
  const placeholderMap = {
    java: '请在此编写 Java 代码...',
    c: '请在此编写 C 语言代码...',
    cpp: '请在此编写 C++ 代码...',
    'c++': '请在此编写 C++ 代码...',
    python: '请在此编写 Python 代码...',
  }
  return placeholderMap[lang] || '请在此编写代码...'
}

// 根据语言生成代码模板（避免在 JS 字符串中使用尖括号，防止 Vue 解析错误）
const LT = String.fromCharCode(60)  // <
const GT = String.fromCharCode(62)  // >
function getCodeTemplate(lang) {
  switch (lang) {
    case 'java':
      return ['public class Main {',
        '    public static void main(String[] args) {',
        '        // 请在此处编写你的代码',
        '    }',
        '}'].join('\n')
    case 'c':
      return ['#include ' + LT + 'stdio.h' + GT, '',
        'int main() {',
        '    // 请在此处编写你的代码',
        '    return 0;',
        '}'].join('\n')
    case 'cpp':
    case 'c++':
      return ['#include ' + LT + 'iostream' + GT,
        'using namespace std;', '',
        'int main() {',
        '    // 请在此处编写你的代码',
        '    return 0;',
        '}'].join('\n')
    case 'python':
    default:
      return '# 请在此处编写你的 Python 代码\n'
  }
}

// localStorage 持久化 key
const timerStorageKey = computed(() => `exam_timer_${examId.value}`)
const answersStorageKey = computed(() => `exam_answers_${examId.value}`)

// 倒计时
const duration = ref(0) // 分钟
const remaining = ref(0) // 剩余秒数
let timer = null
let statusPollingTimer = null // 考试状态降级轮询计时器
let wsConnection = null // WebSocket 连接
let wsReconnectTimer = null // WebSocket 重连计时器
let wsHeartbeatTimer = null // WebSocket 心跳计时器

const remainingMinutes = computed(() => Math.floor(remaining.value / 60))

const formatCountdown = computed(() => {
  const mins = Math.floor(remaining.value / 60)
  const secs = remaining.value % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
})

function startTimer() {
  const totalSeconds = duration.value * 60
  // 尝试从 localStorage 恢复开始时间
  const saved = localStorage.getItem(timerStorageKey.value)
  let startTs = Date.now()
  if (saved) {
    const parsed = JSON.parse(saved)
    if (parsed.examId === examId.value && parsed.startTs) {
      startTs = parsed.startTs
    } else {
      // 新考试，保存开始时间
      localStorage.setItem(timerStorageKey.value, JSON.stringify({ examId: examId.value, startTs }))
    }
  } else {
    // 首次开始，保存
    localStorage.setItem(timerStorageKey.value, JSON.stringify({ examId: examId.value, startTs }))
  }

  timer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTs) / 1000)
    remaining.value = Math.max(0, totalSeconds - elapsed)
    if (remaining.value <= 0) {
      clearInterval(timer)
      handleSubmit(true)
    }
  }, 1000)
}

// 管理端强制结束考试的统一处理函数
function handleExamForceEnd(message) {
  if (examForceEnded.value) return // 防止重复触发
  examForceEnded.value = true
  clearInterval(statusPollingTimer)
  clearInterval(timer)
  closeWebSocket()
  ElMessageBox.alert(
    message || '管理员已结束本次考试，您的答案将自动提交。',
    '考试已结束',
    { confirmButtonText: '确定', type: 'warning' }
  ).then(() => {
    handleSubmit(true)
  })
}

// ========== WebSocket 实时通知 ==========
function connectWebSocket() {
  if (wsConnection && wsConnection.readyState === WebSocket.OPEN) return
  try {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.host
    const wsUrl = `${wsProtocol}//${wsHost}/api/student/exams/${examId.value}/ws`
    wsConnection = new WebSocket(wsUrl)

    wsConnection.onopen = () => {
      // WebSocket 连接成功，停止降级轮询
      if (statusPollingTimer) {
        clearInterval(statusPollingTimer)
        statusPollingTimer = null
      }
      // 启动心跳（每30秒发送一次 ping）
      wsHeartbeatTimer = setInterval(() => {
        if (wsConnection && wsConnection.readyState === WebSocket.OPEN) {
          wsConnection.send('ping')
        }
      }, 30000)
    }

    wsConnection.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'exam_ended') {
          handleExamForceEnd(data.message)
        }
      } catch {
        // 非 JSON 消息（如 pong），忽略
      }
    }

    wsConnection.onclose = () => {
      wsConnection = null
      if (wsHeartbeatTimer) {
        clearInterval(wsHeartbeatTimer)
        wsHeartbeatTimer = null
      }
      // 如果考试还在进行中，启动降级轮询和重连
      if (examStarted.value && !examForceEnded.value && !submitting.value) {
        startFallbackPolling()
        // 5秒后尝试重连 WebSocket
        wsReconnectTimer = setTimeout(() => {
          if (examStarted.value && !examForceEnded.value) {
            connectWebSocket()
          }
        }, 5000)
      }
    }

    wsConnection.onerror = () => {
      // onclose 会自动触发，这里不做处理
    }
  } catch {
    // WebSocket 连接失败，使用降级轮询
    startFallbackPolling()
  }
}

function closeWebSocket() {
  if (wsHeartbeatTimer) {
    clearInterval(wsHeartbeatTimer)
    wsHeartbeatTimer = null
  }
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer)
    wsReconnectTimer = null
  }
  if (wsConnection) {
    wsConnection.onclose = null // 防止触发重连
    wsConnection.close()
    wsConnection = null
  }
}

// 降级轮询（仅在 WebSocket 断开时使用，每5秒检查一次）
function startFallbackPolling() {
  if (statusPollingTimer) clearInterval(statusPollingTimer)
  statusPollingTimer = setInterval(async () => {
    if (!examStarted.value || submitting.value || examForceEnded.value) return
    try {
      const res = await checkExamStatus(examId.value)
      const status = res.data?.status
      if (status === 'finished' || status === 'cancelled') {
        handleExamForceEnd('管理员已结束本次考试，您的答案将自动提交。')
      }
    } catch {
      // 忽略轮询错误
    }
  }, 5000)
}

// 启动考试状态监控（WebSocket 优先 + 降级轮询）
function startStatusMonitoring() {
  connectWebSocket()
  // 同时启动降级轮询作为兜底，WebSocket 连接成功后会停止轮询
  startFallbackPolling()
}

// 持久化答案到 localStorage
function saveAnswers() {
  localStorage.setItem(answersStorageKey.value, JSON.stringify(answers.value))
}

// 从 localStorage 恢复答案
function restoreAnswers() {
  const saved = localStorage.getItem(answersStorageKey.value)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      answers.value = parsed
    } catch { /* ignore */ }
  }
}

// 页面关闭/刷新前保存答案
function handleBeforeUnload(e) {
  if (examStarted.value && !submitting.value) {
    saveAnswers()
    e.preventDefault()
    e.returnValue = ''
  }
}

// 路由离开守卫
onBeforeRouteLeave((to, from, next) => {
  if (examStarted.value && !submitting.value) {
    ElMessageBox.confirm(
      '确定要离开考试页面吗？离开后将自动提交试卷。',
      '确认交卷',
      { confirmButtonText: '确定交卷', cancelButtonText: '继续答题', type: 'warning' }
    ).then(() => {
      handleSubmit(true).then(() => next())
    }).catch(() => {
      next(false)
    })
  } else {
    next()
  }
})

onMounted(async () => {
  // 注册 beforeunload 事件
  window.addEventListener('beforeunload', handleBeforeUnload)

  try {
    const res = await getExamQuestions(examId.value)
    exam.value = res.data.exam
    questions.value = res.data.questions
    duration.value = res.data.exam.duration || 60
    loaded.value = true

    // 尝试恢复答案
    restoreAnswers()

    // 为编程题预填代码模板（使用每道题的语言设置）
    questions.value.forEach(q => {
      if (q.question_type === 'programming' && !answers.value[q.id]) {
        const lang = q.language || 'python'
        answers.value[q.id] = getCodeTemplate(lang)
      }
    })

    // 检查是否已经开始了考试（刷新恢复）
    const saved = localStorage.getItem(timerStorageKey.value)
    if (saved) {
      const parsed = JSON.parse(saved)
      if (parsed.examId === examId.value && parsed.startTs) {
        const elapsed = Math.floor((Date.now() - parsed.startTs) / 1000)
        const totalSeconds = duration.value * 60
        if (elapsed < totalSeconds) {
          // 还在考试时间内，直接继续
          examStarted.value = true
          startTimer()
          startStatusMonitoring() // 恢复状态监控
          return
        }
      }
    }

    // 首次进入：确认开始
    await ElMessageBox.confirm(
      `考试时长 ${duration.value} 分钟，开始后倒计时将启动，时间到自动提交。`,
      '确认开始考试',
      { confirmButtonText: '开始考试', cancelButtonText: '取消', type: 'warning' }
    )
    examStarted.value = true
    startTimer()
    startStatusMonitoring() // 开始状态监控
  } catch (e) {
    if (e !== 'cancel') {
      // 考试已结束或不可用，显示提示后返回首页
      const detail = e?.response?.data?.detail || e?.message || ''
      if (detail.includes('已结束') || detail.includes('无法获取题目') || detail.includes('已完成')) {
        ElMessage.warning(detail || '该考试已不可用')
        router.replace('/')
      } else if (detail) {
        ElMessage.error(detail)
        router.replace('/')
      }
      // 其他错误由拦截器处理
    } else {
      router.back()
    }
  }
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  if (statusPollingTimer) clearInterval(statusPollingTimer)
  closeWebSocket()
  closeWebSocket()
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

function typeLabel(type) {
  const map = {
    choice: '选择题',
    fill_blank: '填空题',
    short_answer: '简答题',
    true_false: '判断题',
    programming: '编程题',
  }
  return map[type] || type
}

function parseOptions(options) {
  if (!options) return []
  let arr = options
  if (typeof options === 'string') {
    try { arr = JSON.parse(options) } catch { return [] }
  }
  if (!Array.isArray(arr)) return []
  const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
  return arr.map((opt, idx) => {
    let text = ''
    if (typeof opt === 'object' && opt.text) {
      text = opt.text
    } else if (typeof opt === 'string') {
      // 去掉开头的 A. B. 等前缀
      const match = opt.match(/^[A-Za-z][.、．)\s]\s*(.*)/)
      text = match ? match[1] : opt
    } else {
      text = String(opt)
    }
    return { label: labels[idx] || String(idx + 1), text }
  })
}

// 根据选项文字长度判断布局方式
function getOptionLayout(options) {
  const opts = parseOptions(options)
  if (!opts.length) return 'layout-long'
  const maxLen = Math.max(...opts.map(o => (o.text || '').length))
  if (maxLen <= 8) return 'layout-short'    // 短选项：一行排列
  if (maxLen <= 25) return 'layout-medium'   // 中等选项：2行2列
  return 'layout-long'                       // 长选项：一列
}

// 代码编辑器：获取行数
function getLineCount(code) {
  if (!code) return 1
  const count = code.split('\n').length
  return Math.max(count, 1)
}

// 代码编辑器：同步滚动
function syncScroll(questionId) {
  nextTick(() => {
    const textarea = document.querySelector(`[data-qid="${questionId}"] .code-textarea`)
    const lineNumbers = document.querySelector(`[data-qid="${questionId}"] .line-numbers`)
    if (textarea && lineNumbers) {
      lineNumbers.scrollTop = textarea.scrollTop
    }
  })
}

// 运行代码测试
async function handleRunCode(question) {
  const code = answers.value[question.id]
  if (!code || !code.trim()) {
    ElMessage.warning('请先编写代码')
    return
  }
  codeRunning[question.id] = true
  codeResults[question.id] = null
  try {
    const res = await runCode({ code, question_id: question.id })
    codeResults[question.id] = res.data
  } catch (e) {
    codeResults[question.id] = {
      output: '',
      error: e.response?.data?.detail || '代码运行失败',
      correct: false,
      expected: '',
    }
  } finally {
    codeRunning[question.id] = false
  }
}

// 返回按钮处理
async function handleBack() {
  try {
    await ElMessageBox.confirm(
      '确定要返回吗？返回后将自动提交试卷。',
      '确认交卷',
      { confirmButtonText: '确定交卷', cancelButtonText: '继续答题', type: 'warning' }
    )
    await handleSubmit(true)
  } catch { /* 继续答题 */ }
}

async function handleSubmit(auto = false) {
  if (!auto) {
    const unanswered = questions.value.filter(q => !answers.value[q.id] && answers.value[q.id] !== 0)
    if (unanswered.length > 0) {
      try {
        await ElMessageBox.confirm(
          `还有 ${unanswered.length} 道题未作答，确认提交？`,
          '提示',
          { confirmButtonText: '确认提交', cancelButtonText: '继续答题', type: 'warning' }
        )
      } catch {
        return
      }
    }
  }

  if (timer) clearInterval(timer)
  if (statusPollingTimer) clearInterval(statusPollingTimer)
  submitting.value = true
  examStarted.value = false

  try {
    const answerList = questions.value.map(q => ({
      question_id: q.id,
      answer: answers.value[q.id] || '',
    }))
    await submitExam(examId.value, { answers: answerList })
    // 提交成功，清理 localStorage
    localStorage.removeItem(timerStorageKey.value)
    localStorage.removeItem(answersStorageKey.value)
    ElMessage.success('提交成功')
    router.replace(`/exam/${examId.value}/result`)
  } catch (e) {
    // 如果是管理端强制结束导致的提交，不再恢复计时器
    if (examForceEnded.value) {
      const detail = e?.response?.data?.detail || ''
      if (detail.includes('已提交过')) {
        // 已经提交过了（可能管理端强制结束时已清除），直接跳转
        ElMessage.success('答案已提交')
        localStorage.removeItem(timerStorageKey.value)
        localStorage.removeItem(answersStorageKey.value)
        router.replace(`/exam/${examId.value}/result`)
      } else {
        ElMessage.error('提交失败：' + (detail || '考试已结束'))
        router.replace('/')
      }
    } else {
      // 正常提交失败，恢复考试状态
      examStarted.value = true
      if (timer === null) startTimer()
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.exam-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}
.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  margin-bottom: 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}
.exam-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.timer {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}
.timer-warning {
  color: #f56c6c;
  animation: blink 1s infinite;
}
@keyframes blink {
  50% { opacity: 0.5; }
}
.exam-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.question-item :deep(.el-card__body) {
  padding: 20px;
}
.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.question-score {
  color: #e6a23c;
  font-size: 14px;
}
.question-content {
  font-size: 16px;
  margin-bottom: 16px;
  line-height: 1.6;
}
.question-num {
  font-weight: bold;
  color: #409eff;
}
.question-options {
  padding-left: 0;
  text-align: left;
}

/* ========== 选择题/判断题 样式（修复对齐） ========== */
.choice-radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  align-items: flex-start;
}
/* 短选项：一行排列 */
.choice-radio-group.layout-short {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 10px;
}
.choice-radio-group.layout-short :deep(.el-radio) {
  width: auto;
  flex: none;
}
.choice-radio-group.layout-short .choice-option {
  width: auto;
  padding: 8px 16px;
}
/* 中等选项：2行2列 */
.choice-radio-group.layout-medium {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
/* 长选项：单列靠左（默认） */
.choice-radio-group.layout-long {
  flex-direction: column;
}
/* radio 通用样式 */
.choice-radio-group :deep(.el-radio) {
  display: flex;
  align-items: flex-start;
  margin-right: 0;
  height: auto;
  width: 100%;
  text-align: left;
}
.choice-radio-group :deep(.el-radio__input) {
  display: none;
}
.choice-radio-group :deep(.el-radio__label) {
  padding-left: 0;
  font-size: unset;
  flex: 1;
  min-width: 0;
  text-align: left;
}
.choice-option {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-radius: 8px;
  border: 2px solid #e4e7ed;
  transition: all 0.2s ease;
  cursor: pointer;
  width: 100%;
  box-sizing: border-box;
  gap: 12px;
}
.choice-option:hover {
  border-color: #c0c4cc;
  background: #f5f7fa;
}
.choice-option-active {
  border-color: #409eff !important;
  background: #ecf5ff !important;
}
.choice-circle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #f0f2f5;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
  color: #606266;
  transition: all 0.2s ease;
}
.choice-option-active .choice-circle {
  background: #409eff;
  color: #fff;
}
.choice-text {
  font-size: 15px;
  line-height: 1.6;
  color: #303133;
  word-break: break-word;
}
.choice-option-active .choice-text {
  color: #409eff;
  font-weight: 500;
}

/* ========== 编程题样式 ========== */
.programming-lang-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f0f9eb;
  border-radius: 6px;
  border: 1px solid #e1f3d8;
}
.lang-hint-text {
  font-size: 13px;
  color: #67c23a;
  font-weight: 500;
}
.code-editor-wrapper {
  display: flex;
  border: 1px solid #3c3c3c;
  border-radius: 6px;
  overflow: hidden;
  background: #1e1e1e;
  max-height: 400px;
}
.line-numbers {
  padding: 12px 0;
  background: #252526;
  color: #858585;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  text-align: right;
  min-width: 48px;
  user-select: none;
  overflow: hidden;
  border-right: 1px solid #3c3c3c;
}
.line-number {
  padding: 0 12px 0 8px;
  height: 22.4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
.code-textarea {
  flex: 1;
  padding: 12px 16px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  border: none;
  outline: none;
  resize: vertical;
  min-height: 250px;
  tab-size: 4;
  white-space: pre;
  overflow-wrap: normal;
  overflow-x: auto;
}
.code-textarea::placeholder {
  color: #6a9955;
}
.code-textarea::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}
.code-textarea::-webkit-scrollbar-track {
  background: #1e1e1e;
}
.code-textarea::-webkit-scrollbar-thumb {
  background: #424242;
  border-radius: 5px;
}
.code-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}
.code-result-panel {
  margin-top: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}
.code-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f5f7fa;
  font-weight: bold;
  font-size: 14px;
  color: #303133;
}
.code-result-body {
  padding: 12px 16px;
}
.code-result-body pre {
  margin: 4px 0 0 0;
  padding: 8px 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 6px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}
.code-error pre {
  color: #f56c6c;
}
.code-output {
  margin-bottom: 12px;
}
.code-output strong,
.code-expected strong,
.code-error strong {
  font-size: 13px;
  color: #606266;
}

.exam-footer {
  text-align: center;
  margin-top: 24px;
  padding-bottom: 40px;
}
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  color: #909399;
}
</style>
