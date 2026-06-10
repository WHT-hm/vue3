<template>
  <div class="exams-container">
    <!-- 搜索和操作区 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="考试名称" clearable style="width: 180px" @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="科目">
          <el-input v-model="filters.subject" placeholder="科目" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="即将开始" value="upcoming" />
            <el-option label="进行中" value="ongoing" />
            <el-option label="已结束" value="finished" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.exam_type" placeholder="全部" clearable style="width: 120px">
            <el-option label="正式考试" value="formal" />
            <el-option label="模拟考试" value="mock" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="resetFilters" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
      <div class="action-bar">
        <el-button type="primary" @click="openDialog('add')" :icon="Plus">创建考试</el-button>
        <el-button type="warning" @click="openExportDialog" :icon="Download">数据导出</el-button>
        <el-button type="success" @click="loadData" :icon="Refresh">刷新</el-button>
      </div>
    </el-card>

    <!-- 考试列表 -->
    <el-card shadow="hover" style="margin-top: 16px; border-radius: 12px">
      <el-table :data="tableData" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="考试名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="subject" label="科目" width="100" />
        <el-table-column prop="exam_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.exam_type === 'formal' ? 'primary' : 'warning'" size="small">
              {{ row.exam_type === 'formal' ? '正式' : '模拟' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试时间" width="160" align="center">
          <template #default="{ row }">{{ formatDate(row.exam_date) }}</template>
        </el-table-column>
        <el-table-column prop="duration" label="时长" width="80" align="center">
          <template #default="{ row }">{{ row.duration ? row.duration + '分钟' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="location" label="地点" width="120" show-overflow-tooltip />
        <el-table-column prop="total_score" label="总分" width="70" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="examStatusMap[row.status]?.type || 'info'" size="small">
              {{ examStatusMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="registered_count" label="报名数" width="80" align="center" />
        <el-table-column prop="avg_score" label="平均分" width="80" align="center">
          <template #default="{ row }">{{ row.avg_score ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.pass_rate != null">{{ row.pass_rate }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="380" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'upcoming' || row.status === 'cancelled'"
              type="success" link size="small"
              @click="handleStartExam(row)"
            >
              <el-icon><VideoPlay /></el-icon> 开始考试
            </el-button>
            <el-button
              v-if="row.status === 'ongoing'"
              type="warning" link size="small"
              @click="handleEndExam(row)"
            >
              <el-icon><VideoPause /></el-icon> 结束考试
            </el-button>
            <el-button
              v-if="row.status === 'finished'"
              type="warning" link size="small"
              @click="handleRetakeExam(row)"
            >
              <el-icon><RefreshRight /></el-icon> 重新考试
            </el-button>
            <el-button type="primary" link size="small" @click="openDialog('edit', row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button type="info" link size="small" @click="viewDetail(row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '创建考试' : '编辑考试'" width="650px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="考试名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入考试名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="科目" prop="subject">
              <el-input v-model="form.subject" placeholder="请输入科目" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="考试类型" prop="exam_type">
              <el-select v-model="form.exam_type" style="width: 100%">
                <el-option label="正式考试" value="formal" />
                <el-option label="模拟考试" value="mock" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考试时间" prop="exam_date">
              <el-date-picker v-model="form.exam_date" type="datetime" placeholder="选择日期时间" style="width: 100%" value-format="YYYY-MM-DDTHH:mm:ss" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="考试时长" prop="duration">
              <el-input-number v-model="form.duration" :min="1" :max="600" placeholder="分钟" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="考试地点" prop="location">
              <el-input v-model="form.location" placeholder="请输入考试地点" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="总分" prop="total_score">
              <el-input-number v-model="form.total_score" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="及格分数" prop="pass_score">
              <el-input-number v-model="form.pass_score" :min="0" :max="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="即将开始" value="upcoming" />
                <el-option label="进行中" value="ongoing" />
                <el-option label="已结束" value="finished" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大人数" prop="max_participants">
              <el-input-number v-model="form.max_participants" :min="1" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="考试描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="考试描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button
          v-if="dialogType === 'add'"
          type="warning"
          @click="handleCreateAndEditQuestions"
          :loading="submitLoading"
        >
          <el-icon><Notebook /></el-icon> 创建并编辑题目
        </el-button>
        <el-button
          v-if="dialogType === 'edit' && currentRow"
          type="warning"
          @click="openQuestionEditor"
        >
          <el-icon><Notebook /></el-icon> 编辑考试题目
        </el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ dialogType === 'add' ? '确认创建' : '确认修改' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 题目编辑器 -->
    <QuestionEditor
      ref="questionEditorRef"
      :exam-id="currentRow?.id"
      :exam-name="currentRow?.name || ''"
      @close="onQuestionEditorClose"
    />

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="考试详情" width="600px">
      <el-descriptions :column="2" border v-if="currentRow">
        <el-descriptions-item label="ID">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="考试名称">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="科目">{{ currentRow.subject }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="currentRow.exam_type === 'formal' ? 'primary' : 'warning'" size="small">
            {{ currentRow.exam_type === 'formal' ? '正式' : '模拟' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="考试时间">{{ formatDate(currentRow.exam_date) }}</el-descriptions-item>
        <el-descriptions-item label="时长">{{ currentRow.duration ? currentRow.duration + '分钟' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="地点">{{ currentRow.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="examStatusMap[currentRow.status]?.type || 'info'" size="small">
            {{ examStatusMap[currentRow.status]?.label || currentRow.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总分">{{ currentRow.total_score }}</el-descriptions-item>
        <el-descriptions-item label="及格分">{{ currentRow.pass_score }}</el-descriptions-item>
        <el-descriptions-item label="报名数">{{ currentRow.registered_count }}</el-descriptions-item>
        <el-descriptions-item label="成绩数">{{ currentRow.scored_count }}</el-descriptions-item>
        <el-descriptions-item label="平均分">{{ currentRow.avg_score ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="通过率">{{ currentRow.pass_rate != null ? currentRow.pass_rate + '%' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="最高分">{{ currentRow.highest_score ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="最低分">{{ currentRow.lowest_score ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="最大人数">{{ currentRow.max_participants || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentRow.description || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 数据导出对话框 -->
    <el-dialog v-model="exportVisible" title="数据导出" width="450px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="选择考试">
          <el-select v-model="exportForm.examId" placeholder="请选择考试" style="width: 100%" filterable>
            <el-option
              v-for="e in tableData"
              :key="e.id"
              :label="`${e.name} (${e.subject})`"
              :value="e.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="导出内容">
          <el-radio-group v-model="exportForm.type">
            <el-radio value="participants">考试人员</el-radio>
            <el-radio value="scores">考试成绩</el-radio>
            <el-radio value="all">人员 + 成绩</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportVisible = false">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="exportLoading" :icon="Download">
          导出 Excel
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { getExams, createExam, updateExam, deleteExam, startExam, endExam, retakeExam, exportParticipants, exportScores, exportAll } from '../api/exams'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Refresh, Plus, Notebook, VideoPlay, VideoPause, RefreshRight, Download } from '@element-plus/icons-vue'
import QuestionEditor from '../components/QuestionEditor.vue'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const dialogType = ref('add')
const currentRow = ref(null)
const formRef = ref(null)
const questionEditorRef = ref(null)

// 导出相关
const exportVisible = ref(false)
const exportLoading = ref(false)
const exportForm = reactive({ examId: null, type: 'all' })

const examStatusMap = {
  upcoming: { label: '即将开始', type: 'success' },
  ongoing: { label: '进行中', type: 'primary' },
  finished: { label: '已结束', type: 'info' },
  cancelled: { label: '已取消', type: 'danger' },
}

const filters = reactive({ keyword: '', subject: '', status: '', exam_type: '' })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const form = reactive({
  name: '', subject: '', exam_type: 'formal', exam_date: '', duration: 120,
  location: '', total_score: 100, pass_score: 60, status: 'upcoming',
  description: '', max_participants: null,
})

const formRules = {
  name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  subject: [{ required: true, message: '请输入科目', trigger: 'blur' }],
  exam_date: [{ required: true, message: '请选择考试时间', trigger: 'change' }],
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const resetForm = () => {
  Object.assign(form, {
    name: '', subject: '', exam_type: 'formal', exam_date: '', duration: 120,
    location: '', total_score: 100, pass_score: 60, status: 'upcoming',
    description: '', max_participants: null,
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.subject) params.subject = filters.subject
    if (filters.status) params.status = filters.status
    if (filters.exam_type) params.exam_type = filters.exam_type

    const res = await getExams(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    console.error('加载考试数据失败:', e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; loadData() }
const resetFilters = () => { Object.assign(filters, { keyword: '', subject: '', status: '', exam_type: '' }); pagination.page = 1; loadData() }

const openDialog = (type, row = null) => {
  dialogType.value = type
  if (type === 'add') {
    resetForm()
  } else {
    Object.assign(form, {
      name: row.name, subject: row.subject, exam_type: row.exam_type,
      exam_date: row.exam_date, duration: row.duration, location: row.location,
      total_score: row.total_score, pass_score: row.pass_score, status: row.status,
      description: row.description, max_participants: row.max_participants,
    })
    currentRow.value = row
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (dialogType.value === 'add') {
        await createExam({ ...form })
        ElMessage.success('考试创建成功')
      } else {
        await updateExam(currentRow.value.id, { ...form })
        ElMessage.success('考试信息更新成功')
      }
      dialogVisible.value = false
      loadData()
    } catch (e) {
      console.error('提交失败:', e)
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除考试「${row.name}」吗？`, '删除确认', {
      confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning',
    })
    await deleteExam(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch { /* 取消 */ }
}

const viewDetail = (row) => { currentRow.value = row; detailVisible.value = true }

// 开始考试
const handleStartExam = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要开始考试「${row.name}」吗？开始后考试状态将变为进行中。`, '开始考试', {
      confirmButtonText: '确定开始', cancelButtonText: '取消', type: 'info',
    })
    const res = await startExam(row.id)
    ElMessage.success(res.message || '考试已开始')
    loadData()
  } catch (e) {
    if (e !== 'cancel' && e?.response?.data?.detail) {
      ElMessage.error(e.response.data.detail)
    }
  }
}

// 结束考试
const handleEndExam = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要结束考试「${row.name}」吗？结束后学员将无法继续作答。`, '结束考试', {
      confirmButtonText: '确定结束', cancelButtonText: '取消', type: 'warning',
    })
    const res = await endExam(row.id)
    ElMessage.success(res.message || '考试已结束')
    loadData()
  } catch (e) {
    if (e !== 'cancel' && e?.response?.data?.detail) {
      ElMessage.error(e.response.data.detail)
    }
  }
}

// 重新考试
const handleRetakeExam = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新开始考试「${row.name}」吗？\n这将清除所有学员的成绩和答题记录，考试状态将变为进行中。`,
      '重新考试确认',
      { confirmButtonText: '确定重新开始', cancelButtonText: '取消', type: 'warning' }
    )
    const res = await retakeExam(row.id)
    ElMessage.success(res.message || '考试已重置')
    loadData()
  } catch (e) {
    if (e !== 'cancel' && e?.response?.data?.detail) {
      ElMessage.error(e.response.data.detail)
    }
  }
}

// 创建考试并打开题目编辑器
const handleCreateAndEditQuestions = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const res = await createExam({ ...form })
      currentRow.value = res
      ElMessage.success('考试创建成功，请编辑考试题目')
      dialogVisible.value = false
      nextTick(() => {
        questionEditorRef.value?.open()
      })
      loadData()
    } catch (e) {
      console.error('创建考试失败:', e)
    } finally {
      submitLoading.value = false
    }
  })
}

// 打开题目编辑器
const openQuestionEditor = () => {
  dialogVisible.value = false
  nextTick(() => {
    questionEditorRef.value?.open()
  })
}

// 题目编辑器关闭后重新打开编辑弹窗（仅编辑模式）
const onQuestionEditorClose = () => {
  if (dialogType.value === 'edit') {
    dialogVisible.value = true
  }
}

// 打开导出对话框
const openExportDialog = () => {
  exportForm.examId = null
  exportForm.type = 'all'
  exportVisible.value = true
}

// 执行导出
const handleExport = async () => {
  if (!exportForm.examId) {
    ElMessage.warning('请选择要导出的考试')
    return
  }

  exportLoading.value = true
  try {
    let res
    if (exportForm.type === 'participants') {
      res = await exportParticipants(exportForm.examId)
    } else if (exportForm.type === 'scores') {
      res = await exportScores(exportForm.examId)
    } else {
      res = await exportAll(exportForm.examId)
    }

    // 从响应头获取文件名，否则使用默认名
    const contentDisposition = res.headers?.['content-disposition'] || ''
    let filename = '导出数据.xlsx'
    const match = contentDisposition.match(/filename\*=UTF-8''(.+)/i)
    if (match) {
      filename = decodeURIComponent(match[1])
    }

    // 创建下载链接
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('导出成功')
    exportVisible.value = false
  } catch (e) {
    console.error('导出失败:', e)
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

onMounted(() => { loadData() })
</script>

<style scoped>
.exams-container { min-height: 100%; }
.filter-card { border-radius: 12px; }
.filter-form { display: flex; flex-wrap: wrap; align-items: center; }
.action-bar { margin-top: 12px; display: flex; gap: 8px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
