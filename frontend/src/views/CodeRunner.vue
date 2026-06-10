<template>
  <div class="code-runner-container">
    <!-- 顶部标题栏 -->
    <div class="top-bar">
      <div class="top-bar-left">
        <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h2 class="page-title">{{ questionTitle || '编程题' }}</h2>
      </div>
      <div class="top-bar-right">
        <el-select v-model="language" style="width: 140px" @change="onLanguageChange">
          <el-option label="Python" value="python" />
          <el-option label="C 语言" value="c" />
          <el-option label="Java" value="java" />
        </el-select>
        <el-tag type="info" size="large">分值：{{ score }}分</el-tag>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧：题目描述 -->
      <div class="left-panel">
        <div class="panel-header">
          <el-icon><Document /></el-icon> 题目描述
        </div>
        <div class="question-desc">
          <div class="desc-content">{{ questionContent || '暂无题目描述' }}</div>

          <div v-if="testCasesDisplay.length > 0" class="test-cases-section">
            <h4>测试用例示例</h4>
            <div v-for="(tc, i) in testCasesDisplay.slice(0, 3)" :key="i" class="test-case-item">
              <div class="tc-row">
                <span class="tc-label">输入：</span>
                <code class="tc-value">{{ tc.input || '(无)' }}</code>
              </div>
              <div class="tc-row">
                <span class="tc-label">期望输出：</span>
                <code class="tc-value">{{ tc.expected_output }}</code>
              </div>
            </div>
          </div>
        </div>

        <!-- 测试结果区域 -->
        <div v-if="testResults" class="results-section">
          <div class="panel-header result-header">
            <el-icon><DataAnalysis /></el-icon> 测试结果
            <el-tag
              :type="testResults.score >= 60 ? 'success' : 'danger'"
              size="large"
              style="margin-left: auto;"
            >
              得分：{{ testResults.score }}分
            </el-tag>
          </div>
          <div class="result-summary">
            <span>通过：<strong :class="testResults.passed === testResults.total ? 'text-success' : 'text-danger'">{{ testResults.passed }}</strong> / {{ testResults.total }}</span>
            <el-progress
              :percentage="testResults.total > 0 ? Math.round(testResults.passed / testResults.total * 100) : 0"
              :color="testResults.passed === testResults.total ? '#67c23a' : '#e6a23c'"
              :stroke-width="10"
              style="margin-top: 8px;"
            />
          </div>
          <div class="result-details">
            <div
              v-for="(r, i) in testResults.results"
              :key="i"
              class="result-item"
              :class="{ 'result-pass': r.passed, 'result-fail': !r.passed }"
            >
              <div class="result-item-header">
                <el-tag :type="r.passed ? 'success' : 'danger'" size="small">
                  {{ r.passed ? '✓ 通过' : '✗ 未通过' }}
                </el-tag>
                <span>测试用例 #{{ i + 1 }}</span>
              </div>
              <div class="result-item-body">
                <div v-if="r.input" class="ri-row">
                  <span>输入：</span><code>{{ r.input }}</code>
                </div>
                <div class="ri-row">
                  <span>期望：</span><code>{{ r.expected_output }}</code>
                </div>
                <div class="ri-row">
                  <span>实际：</span><code :class="{ 'text-danger': !r.passed }">{{ r.actual_output }}</code>
                </div>
                <div v-if="r.error" class="ri-row ri-error">
                  <span>错误：</span><code>{{ r.error }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：代码编辑器 -->
      <div class="right-panel">
        <div class="editor-toolbar">
          <div class="toolbar-left">
            <span class="editor-label">
              <el-icon><EditPen /></el-icon> 代码编辑器
            </span>
          </div>
          <div class="toolbar-right">
            <el-button type="success" @click="runCode" :loading="running" :icon="VideoPlay">
              {{ running ? '运行中...' : '运行测试' }}
            </el-button>
            <el-button type="primary" @click="submitCode" :loading="submitting" :icon="Check">
              {{ submitting ? '提交中...' : '提交答案' }}
            </el-button>
          </div>
        </div>
        <div class="editor-wrapper">
          <MonacoEditor
            v-model="code"
            :language="language"
            :theme="editorTheme"
            :height="editorHeight"
            :options="editorOptions"
          />
        </div>

        <!-- 输出控制台 -->
        <div class="console-section">
          <div class="console-header">
            <el-icon><Monitor /></el-icon> 输出控制台
            <el-button size="small" text @click="consoleOutput = ''">清空</el-button>
          </div>
          <pre class="console-body" :class="{ 'console-error': hasError }">{{ consoleOutput || '等待运行...' }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, Document, EditPen, VideoPlay,
  Check, Monitor, DataAnalysis
} from '@element-plus/icons-vue'
import MonacoEditor from '../components/MonacoEditorWrapper.vue'
import { executeCode } from '../api/questions'

const route = useRoute()
const router = useRouter()

// 从路由参数获取题目信息
const questionId = computed(() => route.params.id || route.query.id)
const questionTitle = ref(route.query.title || '编程题')
const questionContent = ref(route.query.content || '')
const score = ref(Number(route.query.score) || 0)
const testCases = ref(route.query.testCases || '[]')
const testCasesDisplay = computed(() => {
  try { return JSON.parse(testCases.value) } catch { return [] }
})

const language = ref(route.query.language || 'python')
const codeTemplates = {
  python: '# 请在此处编写你的代码\n',
  c: '#include <stdio.h>\n\nint main() {\n    // 请在此处编写你的代码\n    return 0;\n}\n',
  java: 'public class Solution {\n    public static void main(String[] args) {\n        // 请在此处编写你的代码\n    }\n}\n',
}
const code = ref(codeTemplates[language.value] || codeTemplates.python)
const running = ref(false)
const submitting = ref(false)
const consoleOutput = ref('')
const hasError = ref(false)
const testResults = ref(null)
const editorTheme = ref('vs-dark')

const editorHeight = ref('400px')
const editorOptions = {
  minimap: { enabled: false },
  fontSize: 14,
  lineNumbers: 'on',
  wordWrap: 'on',
  automaticLayout: true,
  scrollBeyondLastLine: false,
  tabSize: 4,
}

// 语言切换时更新默认代码
const onLanguageChange = (lang) => {
  code.value = codeTemplates[lang] || codeTemplates.python
}

// 返回上一页（新标签页打开时关闭窗口，否则返回上一页）
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    window.close()
  }
}

// 运行代码
const runCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码')
    return
  }
  running.value = true
  consoleOutput.value = '正在运行...\n'
  hasError.value = false
  testResults.value = null

  try {
    const res = await executeCode({
      code: code.value,
      language: language.value,
      test_cases: testCases.value,
    })

    const data = res.data
    testResults.value = data

    if (data.results && data.results.length > 0) {
      let output = ''
      data.results.forEach((r, i) => {
        output += `\n--- 测试用例 #${i + 1} ---\n`
        if (r.input) output += `输入: ${r.input}\n`
        output += `期望: ${r.expected_output}\n`
        output += `实际: ${r.actual_output}\n`
        output += `结果: ${r.passed ? '✓ 通过' : '✗ 未通过'}\n`
        if (r.error) {
          output += `错误: ${r.error}\n`
          hasError.value = true
        }
      })
      output += `\n====================\n`
      output += `通过: ${data.passed}/${data.total} | 得分: ${data.score}分\n`
      consoleOutput.value = output
    } else if (data.results && data.results.length === 1 && !testCasesDisplay.value.length) {
      const r = data.results[0]
      if (r.error) {
        consoleOutput.value = `运行错误:\n${r.error}`
        hasError.value = true
      } else {
        consoleOutput.value = `运行输出:\n${r.output || '(无输出)'}`
      }
    }

    if (data.score > 0) {
      ElMessage.success(`测试完成！得分：${data.score}分`)
    }
  } catch (e) {
    consoleOutput.value = `请求失败: ${e.message || '未知错误'}`
    hasError.value = true
  } finally {
    running.value = false
  }
}

// 提交答案
const submitCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请先编写代码')
    return
  }

  submitting.value = true
  consoleOutput.value = '正在提交并测试...\n'
  testResults.value = null
  hasError.value = false

  try {
    const res = await executeCode({
      code: code.value,
      language: language.value,
      test_cases: testCases.value,
    })

    const data = res.data
    testResults.value = data

    let output = '===== 提交结果 =====\n\n'
    if (data.results) {
      data.results.forEach((r, i) => {
        output += `测试 #${i + 1}: ${r.passed ? '✓ 通过' : '✗ 未通过'}\n`
        if (r.error) {
          output += `  错误: ${r.error}\n`
          hasError.value = true
        }
      })
    }
    output += `\n通过: ${data.passed}/${data.total}\n`
    output += `最终得分: ${data.score}分\n`
    consoleOutput.value = output

    if (data.score >= 60) {
      ElMessage.success(`提交成功！得分：${data.score}分`)
    } else {
      ElMessage.warning(`得分：${data.score}分，请继续努力！`)
    }
  } catch (e) {
    consoleOutput.value = `提交失败: ${e.message || '未知错误'}`
    hasError.value = true
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // 根据窗口高度调整编辑器
  const h = window.innerHeight - 300
  editorHeight.value = Math.max(300, h) + 'px'
})
</script>

<style scoped>
.code-runner-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  color: #d4d4d4;
  overflow: hidden;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #2d2d2d;
  border-bottom: 1px solid #404040;
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 16px;
  color: #e0e0e0;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧面板 */
.left-panel {
  width: 40%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #404040;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: #252526;
  font-weight: 600;
  font-size: 14px;
  color: #cccccc;
  border-bottom: 1px solid #404040;
}

.result-header {
  width: 100%;
}

.question-desc {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

.desc-content {
  font-size: 14px;
  line-height: 1.8;
  color: #d4d4d4;
  white-space: pre-wrap;
}

.test-cases-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #404040;
}

.test-cases-section h4 {
  margin: 0 0 12px 0;
  color: #e0e0e0;
  font-size: 14px;
}

.test-case-item {
  background: #1e1e1e;
  border-radius: 6px;
  padding: 10px 12px;
  margin-bottom: 8px;
}

.tc-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 4px;
}

.tc-label {
  color: #909399;
  min-width: 70px;
  font-size: 13px;
}

.tc-value {
  background: #2d2d2d;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  color: #9cdcfe;
}

/* 结果区域 */
.results-section {
  border-top: 1px solid #404040;
}

.result-summary {
  padding: 12px 16px;
  font-size: 14px;
  color: #d4d4d4;
}

.result-details {
  padding: 0 16px 16px;
  max-height: 300px;
  overflow-y: auto;
}

.result-item {
  border-radius: 6px;
  margin-bottom: 8px;
  overflow: hidden;
}

.result-pass {
  border: 1px solid #2d6a2d;
}

.result-fail {
  border: 1px solid #6a2d2d;
}

.result-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #252526;
  font-size: 13px;
}

.result-item-body {
  padding: 8px 12px;
  font-size: 13px;
  background: #1e1e1e;
}

.ri-row {
  margin-bottom: 4px;
  display: flex;
  align-items: flex-start;
}

.ri-row span {
  color: #909399;
  min-width: 50px;
}

.ri-row code {
  color: #9cdcfe;
}

.ri-error code {
  color: #f48771;
}

.text-success {
  color: #67c23a;
}

.text-danger {
  color: #f56c6c;
}

/* 右侧面板 */
.right-panel {
  width: 60%;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #252526;
  border-bottom: 1px solid #404040;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.editor-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 14px;
  color: #cccccc;
}

.editor-wrapper {
  flex: 1;
}

/* 控制台 */
.console-section {
  border-top: 1px solid #404040;
  max-height: 200px;
  display: flex;
  flex-direction: column;
}

.console-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 16px;
  background: #252526;
  font-size: 13px;
  font-weight: 600;
  color: #cccccc;
  justify-content: space-between;
}

.console-body {
  flex: 1;
  margin: 0;
  padding: 8px 16px;
  background: #1a1a1a;
  color: #4ec9b0;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-y: auto;
  white-space: pre-wrap;
}

.console-error {
  color: #f48771;
}
</style>
