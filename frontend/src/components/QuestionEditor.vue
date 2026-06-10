<template>
  <el-dialog
    v-model="visible"
    :title="`编辑考试题目 - ${examName}`"
    width="900px"
    destroy-on-close
    @close="handleClose"
  >
    <!-- 顶部操作栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="addQuestion">
          <el-icon><Plus /></el-icon> 添加题目
        </el-button>
        <el-button type="success" @click="triggerImport">
          <el-icon><Upload /></el-icon> 导入题库
        </el-button>
        <input
          ref="fileInputRef"
          type="file"
          accept=".json"
          style="display: none"
          @change="handleFileImport"
        />
      </div>
      <div class="toolbar-right">
        <el-tag type="info">共 {{ questions.length }} 道题</el-tag>
        <el-tag type="warning">总分: {{ totalScore }}</el-tag>
      </div>
    </div>

    <!-- 题目列表 -->
    <div class="question-list" v-loading="loading">
      <el-empty v-if="questions.length === 0 && !loading" description="暂无题目，请添加或导入" />

      <div
        v-for="(q, index) in questions"
        :key="q.id || q._tempId"
        class="question-item"
      >
        <div class="question-header">
          <div class="question-index">
            <el-tag :type="questionTypeMap[q.question_type]?.tagType || 'info'" size="small">
              {{ questionTypeMap[q.question_type]?.label || '未知' }}
            </el-tag>
            <span class="index-text">第 {{ index + 1 }} 题</span>
            <span class="score-text">（{{ q.score }}分）</span>
          </div>
          <div class="question-actions">
            <el-button size="small" @click="moveUp(index)" :disabled="index === 0" link>
              <el-icon><Top /></el-icon>
            </el-button>
            <el-button size="small" @click="moveDown(index)" :disabled="index === questions.length - 1" link>
              <el-icon><Bottom /></el-icon>
            </el-button>
            <el-button type="primary" size="small" link @click="editQuestion(index)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button type="danger" size="small" link @click="removeQuestion(index)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </div>
        <div class="question-content">{{ q.content || '(未填写题目内容)' }}</div>
        <div v-if="q.question_type === 'choice' && q.options" class="question-options">
          <template v-for="(opt, oi) in parseOptions(q.options)" :key="oi">
            <div class="option-item" :class="{ 'is-answer': q.answer === String.fromCharCode(65 + oi) }">
              <span class="option-label">{{ String.fromCharCode(65 + oi) }}.</span>
              <span>{{ opt }}</span>
              <el-tag v-if="q.answer === String.fromCharCode(65 + oi)" type="success" size="small" style="margin-left: 4px">正确答案</el-tag>
            </div>
          </template>
        </div>
        <div v-if="q.question_type === 'true_false' && q.answer" class="question-answer">
          答案：<el-tag :type="q.answer === '对' || q.answer === '正确' ? 'success' : 'danger'" size="small">{{ q.answer }}</el-tag>
        </div>
        <div v-if="q.answer && q.question_type !== 'choice' && q.question_type !== 'true_false' && q.question_type !== 'programming' && q.question_type !== 'judge'" class="question-answer">
          答案：{{ q.answer }}
        </div>
        <div v-if="q.question_type === 'programming'" class="question-actions-extra">
          <el-button type="success" size="small" @click="openCodeRunner(q)">
            <el-icon><Monitor /></el-icon> 打开编程环境
          </el-button>
          <span v-if="q.answer" class="lang-info">语言: {{ {python:'Python',c:'C 语言',java:'Java'}[q.answer] || q.answer }}</span>
          <span v-if="q.options" class="tc-info">测试用例: {{ parseOptions(q.options).length }} 个</span>
        </div>
        <div v-if="q.analysis" class="question-analysis">
          解析：{{ q.analysis }}
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="saveAll" :loading="saving">保存全部</el-button>
    </template>
  </el-dialog>

  <!-- 单个题目编辑弹窗 -->
  <el-dialog
    v-model="editVisible"
    :title="editIndex === -1 ? '添加题目' : '编辑题目'"
    width="650px"
    append-to-body
    destroy-on-close
  >
    <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="100px">
      <el-form-item label="题目类型" prop="question_type">
        <el-select v-model="editForm.question_type" style="width: 100%" @change="onTypeChange">
          <el-option v-for="(item, key) in questionTypeMap" :key="key" :label="item.label" :value="key" />
        </el-select>
      </el-form-item>
      <el-form-item label="题目内容" prop="content">
        <el-input v-model="editForm.content" type="textarea" :rows="4" placeholder="请输入题目内容" />
      </el-form-item>

      <!-- 选择题选项 -->
      <template v-if="editForm.question_type === 'choice'">
        <el-form-item label="选项">
          <div class="edit-options">
            <div v-for="(opt, oi) in editOptions" :key="oi" class="edit-option-item">
              <span class="option-label-edit">{{ String.fromCharCode(65 + oi) }}.</span>
              <el-input v-model="editOptions[oi]" placeholder="请输入选项内容" style="flex: 1" />
              <el-button
                type="danger"
                link
                @click="editOptions.splice(oi, 1)"
                :disabled="editOptions.length <= 2"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button size="small" @click="editOptions.push('')" :disabled="editOptions.length >= 8">
              <el-icon><Plus /></el-icon> 添加选项
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="正确答案" prop="answer">
          <el-select v-model="editForm.answer" placeholder="请选择正确答案" style="width: 200px">
            <el-option
              v-for="(opt, oi) in editOptions"
              :key="oi"
              :label="String.fromCharCode(65 + oi)"
              :value="String.fromCharCode(65 + oi)"
            />
          </el-select>
        </el-form-item>
      </template>

      <!-- 判断题答案 -->
      <template v-if="editForm.question_type === 'true_false'">
        <el-form-item label="正确答案" prop="answer">
          <el-radio-group v-model="editForm.answer">
            <el-radio value="正确">正确</el-radio>
            <el-radio value="错误">错误</el-radio>
          </el-radio-group>
        </el-form-item>
      </template>

      <!-- 填空题答案 -->
      <template v-if="editForm.question_type === 'fill_blank'">
        <el-form-item label="正确答案" prop="answer">
          <el-input v-model="editForm.answer" placeholder="请输入正确答案（多个答案用 | 分隔）" />
        </el-form-item>
      </template>

      <!-- 简答题答案 -->
      <template v-if="editForm.question_type === 'short_answer'">
        <el-form-item label="参考答案" prop="answer">
          <el-input v-model="editForm.answer" type="textarea" :rows="3" placeholder="请输入参考答案" />
        </el-form-item>
      </template>

      <!-- 编程题配置 -->
      <template v-if="editForm.question_type === 'programming'">
        <el-form-item label="编程语言">
          <el-select v-model="editForm.answer" style="width: 200px" placeholder="选择默认语言">
            <el-option label="Python" value="python" />
            <el-option label="C 语言" value="c" />
            <el-option label="Java" value="java" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试用例">
          <div class="edit-testcases">
            <div v-for="(tc, ti) in editTestCases" :key="ti" class="edit-tc-item">
              <div class="tc-input-row">
                <span class="tc-label">输入:</span>
                <el-input v-model="tc.input" placeholder="输入数据（可为空）" style="flex: 1" />
              </div>
              <div class="tc-input-row">
                <span class="tc-label">期望输出:</span>
                <el-input v-model="tc.expected_output" placeholder="期望的输出结果" style="flex: 1" />
              </div>
              <el-button type="danger" link @click="editTestCases.splice(ti, 1)">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </div>
            <el-button size="small" @click="editTestCases.push({ input: '', expected_output: '' })">
              <el-icon><Plus /></el-icon> 添加测试用例
            </el-button>
          </div>
        </el-form-item>
      </template>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="分值" prop="score">
            <el-input-number v-model="editForm.score" :min="0" :max="1000" :precision="1" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="排序号">
            <el-input-number v-model="editForm.order_num" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="解析">
        <el-input v-model="editForm.analysis" type="textarea" :rows="2" placeholder="题目解析（选填）" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="editVisible = false">取消</el-button>
      <el-button type="primary" @click="saveQuestion" :loading="editSaving">
        {{ editIndex === -1 ? '添加' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Edit, Delete, Top, Bottom, Monitor } from '@element-plus/icons-vue'
import {
  getQuestions, createQuestion, updateQuestion,
  deleteQuestion, batchCreateQuestions, importQuestionsFromFile
} from '../api/questions'
import { forceEndExam } from '../api/exams'

const router = useRouter()

const props = defineProps({
  examId: { type: Number, default: null },
  examName: { type: String, default: '' },
})

const emit = defineEmits(['close'])

const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const questions = ref([])
const fileInputRef = ref(null)

// 题目类型映射
const questionTypeMap = {
  choice: { label: '选择题', tagType: 'primary' },
  fill_blank: { label: '填空题', tagType: 'success' },
  short_answer: { label: '简答题', tagType: 'warning' },
  true_false: { label: '判断题', tagType: 'info' },
  programming: { label: '编程题', tagType: '' },
}

const totalScore = computed(() => {
  return questions.value.reduce((sum, q) => sum + (q.score || 0), 0)
})

// 打开弹窗
const open = () => {
  visible.value = true
  loadQuestions()
}

// 加载题目列表
const loadQuestions = async () => {
  if (!props.examId) return
  loading.value = true
  try {
    const res = await getQuestions({ exam_id: props.examId })
    questions.value = res.data || []
  } catch (e) {
    console.error('加载题目失败:', e)
  } finally {
    loading.value = false
  }
}

// 解析选项
const parseOptions = (optionsStr) => {
  if (!optionsStr) return []
  try {
    return JSON.parse(optionsStr)
  } catch {
    return optionsStr.split(',').map(s => s.trim())
  }
}

// 关闭弹窗
const handleClose = () => {
  visible.value = false
  editVisible.value = false
  emit('close')
}

// ============ 题目编辑 ============

const editVisible = ref(false)
const editSaving = ref(false)
const editIndex = ref(-1)
const editFormRef = ref(null)
const editOptions = ref(['', '', '', ''])
const editTestCases = ref([{ input: '', expected_output: '' }])

const editForm = reactive({
  question_type: 'choice',
  content: '',
  answer: '',
  score: 5,
  order_num: 0,
  analysis: '',
})

const editRules = {
  question_type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
}

// 题目类型变化时重置选项和答案
const onTypeChange = (type) => {
  editForm.answer = ''
  if (type === 'choice') {
    editOptions.value = ['', '', '', '']
  } else if (type === 'programming') {
    editForm.answer = 'python'
    editTestCases.value = [{ input: '', expected_output: '' }]
  }
}

// 添加题目
const addQuestion = () => {
  editIndex.value = -1
  Object.assign(editForm, {
    question_type: 'choice',
    content: '',
    answer: '',
    score: 5,
    order_num: questions.value.length + 1,
    analysis: '',
  })
  editOptions.value = ['', '', '', '']
  editTestCases.value = [{ input: '', expected_output: '' }]
  editVisible.value = true
}

// 编辑题目
const editQuestion = (index) => {
  editIndex.value = index
  const q = questions.value[index]
  Object.assign(editForm, {
    question_type: q.question_type,
    content: q.content,
    answer: q.answer || '',
    score: q.score || 0,
    order_num: q.order_num || index + 1,
    analysis: q.analysis || '',
  })
  if (q.question_type === 'choice' && q.options) {
    editOptions.value = parseOptions(q.options)
  } else {
    editOptions.value = ['', '', '', '']
  }
  if (q.question_type === 'programming' && q.options) {
    try {
      editTestCases.value = JSON.parse(q.options)
    } catch {
      editTestCases.value = [{ input: '', expected_output: '' }]
    }
  } else {
    editTestCases.value = [{ input: '', expected_output: '' }]
  }
  editVisible.value = true
}

// 打开编程环境
const openCodeRunner = (q) => {
  const query = {
    title: q.content ? q.content.substring(0, 50) : '编程题',
    content: q.content || '',
    score: q.score || 0,
    testCases: q.options || '[]',
    language: q.answer || 'python',
  }
  const routeData = router.resolve({ path: '/code-runner', query })
  window.open(routeData.href, '_blank')
}

// 保存单个题目
const saveQuestion = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    editSaving.value = true
    try {
      const data = {
        exam_id: props.examId,
        question_type: editForm.question_type,
        content: editForm.content,
        answer: editForm.answer,
        score: editForm.score,
        order_num: editForm.order_num,
        analysis: editForm.analysis,
      }

      // 选择题设置选项
      if (editForm.question_type === 'choice') {
        const validOptions = editOptions.value.filter(o => o.trim() !== '')
        data.options = JSON.stringify(validOptions)
      }

      // 编程题设置测试用例
      if (editForm.question_type === 'programming') {
        const validCases = editTestCases.value.filter(tc => tc.expected_output.trim() !== '')
        data.options = JSON.stringify(validCases)
      }

      if (editIndex.value === -1) {
        // 新增
        const res = await createQuestion(data)
        questions.value.push(res.data)
        ElMessage.success('题目添加成功')
      } else {
        // 更新
        const q = questions.value[editIndex.value]
        const res = await updateQuestion(q.id, data)
        questions.value[editIndex.value] = res.data
        ElMessage.success('题目更新成功')
      }

      editVisible.value = false
    } catch (e) {
      console.error('保存题目失败:', e)
    } finally {
      editSaving.value = false
    }
  })
}

// 删除题目
const removeQuestion = async (index) => {
  try {
    await ElMessageBox.confirm('确定删除该题目吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const q = questions.value[index]
    if (q.id) {
      await deleteQuestion(q.id)
    }
    questions.value.splice(index, 1)
    ElMessage.success('题目已删除')
  } catch { /* 取消 */ }
}

// 上移/下移
const moveUp = (index) => {
  if (index <= 0) return
  const arr = questions.value
  ;[arr[index - 1], arr[index]] = [arr[index], arr[index - 1]]
}

const moveDown = (index) => {
  if (index >= questions.value.length - 1) return
  const arr = questions.value
  ;[arr[index], arr[index + 1]] = [arr[index + 1], arr[index]]
}

const saveAll = async () => {
  saving.value = true
  try {
    // 保存排序号
    for (let i = 0; i < questions.value.length; i++) {
      const q = questions.value[i]
      if (q.id && q.order_num !== i + 1) {
        await updateQuestion(q.id, { order_num: i + 1 })
        q.order_num = i + 1
      }
    }
    // 强制结束考试：清除所有成绩和答题记录，设置状态为已结束
    try {
      await forceEndExam(props.examId)
    } catch (err) {
      console.warn('强制结束考试失败（可能考试未开始）:', err)
    }
    ElMessage.success('保存成功，考试已结束，题库已更新')
    visible.value = false
    router.push('/exams')
  } catch (e) {
    console.error('保存失败:', e)
  } finally {
    saving.value = false
  }
}

// ============ 导入功能 ============

const triggerImport = () => {
  fileInputRef.value?.click()
}

const handleFileImport = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  if (!file.name.endsWith('.json')) {
    ElMessage.error('仅支持 JSON 格式文件')
    return
  }

  try {
    const res = await importQuestionsFromFile(props.examId, file)
    ElMessage.success(res.message || `成功导入 ${res.data?.count || 0} 道题目`)
    loadQuestions()
  } catch (e) {
    console.error('导入失败:', e)
  }

  // 清空文件输入，允许重复选择
  event.target.value = ''
}

defineExpose({ open })
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.toolbar-left {
  display: flex;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.question-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 4px;
}

.question-item {
  padding: 12px 16px;
  margin-bottom: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.2s;
}

.question-item:hover {
  border-color: #409eff;
  background: #f0f7ff;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.question-index {
  display: flex;
  align-items: center;
  gap: 8px;
}

.index-text {
  font-weight: 600;
  color: #303133;
}

.score-text {
  color: #909399;
  font-size: 13px;
}

.question-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.question-content {
  font-size: 14px;
  color: #303133;
  line-height: 1.6;
  margin-bottom: 8px;
  white-space: pre-wrap;
}

.question-options {
  margin-top: 8px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  margin-bottom: 4px;
  border-radius: 4px;
  font-size: 13px;
}

.option-item.is-answer {
  background: #f0f9eb;
  color: #67c23a;
  font-weight: 500;
}

.option-label {
  font-weight: 600;
  margin-right: 8px;
  min-width: 20px;
}

.question-answer {
  font-size: 13px;
  color: #67c23a;
  margin-top: 4px;
}

.question-analysis {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px dashed #e4e7ed;
}

.edit-options {
  width: 100%;
}

.edit-option-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.option-label-edit {
  font-weight: 600;
  min-width: 20px;
}

.question-actions-extra {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e4e7ed;
}

.lang-info, .tc-info {
  font-size: 12px;
  color: #909399;
}

.edit-testcases {
  width: 100%;
}

.edit-tc-item {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 10px;
  margin-bottom: 8px;
}

.tc-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.tc-input-row .tc-label {
  min-width: 65px;
  font-size: 13px;
  color: #606266;
}
</style>
