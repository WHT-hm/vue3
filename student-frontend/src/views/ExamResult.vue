<template>
  <div class="result-container" v-if="loaded">
    <div class="result-header">
      <h2>{{ exam.name }} - 考试结果</h2>
    </div>
    <el-card class="score-card" shadow="hover">
      <div class="score-section">
        <div class="score-item">
          <span class="score-label">实际得分</span>
          <span class="score-value" :class="{ 'pass': result.passed, 'fail': !result.passed }">
            {{ result.score }}
          </span>
        </div>
        <div class="score-item">
          <span class="score-label">总分</span>
          <span class="score-value">{{ exam.total_score }}</span>
        </div>
        <div class="score-item">
          <span class="score-label">状态</span>
          <el-tag :type="result.passed ? 'success' : 'danger'" size="large">
            {{ result.passed ? '及格' : '不及格' }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <h3 class="detail-title">答题详情</h3>
    <div class="detail-list">
      <el-card v-for="(item, idx) in details" :key="item.question_id" class="detail-card" shadow="never">
        <div class="detail-header">
          <el-tag size="small">{{ typeLabel(item.question_type) }}</el-tag>
          <el-tag v-if="item.is_correct === true" type="success" size="small">正确</el-tag>
          <el-tag v-else-if="item.is_correct === false" type="danger" size="small">错误</el-tag>
          <el-tag v-else type="warning" size="small">待批改</el-tag>
          <span class="detail-score">{{ item.score_obtained }} / {{ item.score_total }} 分</span>
        </div>
        <div class="detail-content">
          <span class="detail-num">{{ idx + 1 }}.</span> {{ item.content }}
        </div>
        <div v-if="item.options" class="detail-options">
          <div v-for="opt in parseOptions(item.options)" :key="opt.label" class="option-row">
            {{ opt.label }}. {{ opt.text }}
          </div>
        </div>
        <!-- 编程题特殊展示 -->
        <template v-if="item.question_type === 'programming'">
          <div class="answer-row">
            <span class="answer-label">提交代码：</span>
          </div>
          <pre class="code-block">{{ item.student_answer || '未作答' }}</pre>
          <!-- 运行结果面板 -->
          <div class="exec-result-panel">
            <div class="exec-result-header">
              <span>运行结果</span>
              <el-tag :type="item.is_correct === true ? 'success' : 'danger'" size="small">
                {{ item.is_correct === true ? '运行正确 ✓' : '运行错误 ✗' }}
              </el-tag>
            </div>
            <div class="exec-result-body">
              <div class="exec-output-section">
                <strong>实际输出：</strong>
                <pre class="exec-pre" :class="{ 'output-correct': item.is_correct === true, 'output-wrong': item.is_correct !== true }">{{ item.execution_output || '（无输出）' }}</pre>
              </div>
              <div v-if="item.execution_error" class="exec-output-section">
                <strong>错误信息：</strong>
                <pre class="exec-pre output-error">{{ item.execution_error }}</pre>
              </div>
              <div class="exec-output-section">
                <strong>期望输出：</strong>
                <pre class="exec-pre output-expected">{{ item.correct_answer }}</pre>
              </div>
            </div>
          </div>
        </template>
        <!-- 非编程题正常展示 -->
        <template v-else>
          <div class="answer-row">
            <span class="answer-label">你的答案：</span>
            <span :class="{ 'correct': item.is_correct === true, 'wrong': item.is_correct === false }">
              {{ item.student_answer || '未作答' }}
            </span>
          </div>
          <div class="answer-row">
            <span class="answer-label">正确答案：</span>
            <span class="correct">{{ item.correct_answer }}</span>
          </div>
        </template>
        <div v-if="item.analysis" class="analysis-row">
          <span class="answer-label">解析：</span>
          <span>{{ item.analysis }}</span>
        </div>
      </el-card>
    </div>

    <div class="result-footer">
      <el-button type="primary" size="large" @click="$router.push('/')">返回主页</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExamResult } from '../api/student'

const route = useRoute()
const examId = computed(() => Number(route.params.id))

const loaded = ref(false)
const exam = ref({})
const result = ref({})
const details = ref([])

onMounted(async () => {
  try {
    const res = await getExamResult(examId.value)
    exam.value = res.data.exam
    result.value = res.data
    details.value = res.data.details
    loaded.value = true
  } catch (e) {
    // handled by interceptor
  }
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
  if (typeof options === 'string') {
    try { return JSON.parse(options) } catch { return [] }
  }
  if (Array.isArray(options)) return options
  return []
}
</script>

<style scoped>
.result-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}
.result-header {
  margin-bottom: 20px;
}
.result-header h2 {
  color: #303133;
}
.score-card {
  margin-bottom: 20px;
}
.score-section {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 20px 0;
}
.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.score-label {
  color: #909399;
  font-size: 14px;
}
.score-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}
.score-value.pass {
  color: #67c23a;
}
.score-value.fail {
  color: #f56c6c;
}
.detail-title {
  color: #303133;
  margin: 20px 0 16px;
}
.detail-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-card :deep(.el-card__body) {
  padding: 20px;
}
.detail-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.detail-score {
  margin-left: auto;
  color: #e6a23c;
  font-size: 14px;
}
.detail-content {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 12px;
}
.detail-num {
  font-weight: bold;
  color: #409eff;
}
.detail-options {
  padding: 8px 20px;
  margin-bottom: 12px;
  color: #606266;
  font-size: 14px;
}
.option-row {
  margin: 4px 0;
}
.answer-row {
  margin: 6px 0;
  font-size: 14px;
}
.answer-label {
  color: #909399;
}
.correct {
  color: #67c23a;
}
.wrong {
  color: #f56c6c;
}
.analysis-row {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f4f4f5;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
}
.result-footer {
  text-align: center;
  margin-top: 24px;
  padding-bottom: 40px;
}
.code-block {
  background: #1e1e1e;
  color: #d4d4d4;
  border: 1px solid #3c3c3c;
  border-radius: 6px;
  padding: 12px 16px;
  margin: 8px 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 300px;
  overflow-y: auto;
}
.exec-result-panel {
  margin-top: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}
.exec-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f5f7fa;
  font-weight: bold;
  font-size: 14px;
  color: #303133;
}
.exec-result-body {
  padding: 12px 16px;
}
.exec-output-section {
  margin-bottom: 10px;
}
.exec-output-section:last-child {
  margin-bottom: 0;
}
.exec-output-section strong {
  font-size: 13px;
  color: #606266;
  display: block;
  margin-bottom: 4px;
}
.exec-pre {
  margin: 0;
  padding: 8px 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  border-radius: 6px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 150px;
  overflow-y: auto;
}
.exec-pre.output-correct {
  border-left: 3px solid #67c23a;
}
.exec-pre.output-wrong {
  border-left: 3px solid #f56c6c;
}
.exec-pre.output-error {
  color: #f56c6c;
  border-left: 3px solid #f56c6c;
}
.exec-pre.output-expected {
  color: #67c23a;
  border-left: 3px solid #67c23a;
}
</style>
