<template>
  <div class="scores-container">
    <!-- 搜索和操作区 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="学员">
          <el-select v-model="filters.student_id" placeholder="全部学员" clearable filterable style="width: 180px">
            <el-option v-for="s in studentOptions" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试">
          <el-select v-model="filters.exam_id" placeholder="全部考试" clearable filterable style="width: 200px">
            <el-option v-for="e in examOptions" :key="e.id" :label="e.name" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否及格">
          <el-select v-model="filters.passed" placeholder="全部" clearable style="width: 100px">
            <el-option label="及格" :value="true" />
            <el-option label="不及格" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="resetFilters" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
      <div class="action-bar">
        <el-button type="primary" @click="openDialog('add')" :icon="Plus">录入成绩</el-button>
        <el-button type="warning" @click="openBatchDialog" :icon="Upload">批量录入</el-button>
        <el-button type="success" @click="loadData" :icon="Refresh">刷新</el-button>
      </div>
    </el-card>

    <!-- 成绩列表 -->
    <el-card shadow="hover" style="margin-top: 16px; border-radius: 12px">
      <el-table :data="tableData" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="student_name" label="学员" width="100" />
        <el-table-column prop="exam_name" label="考试" min-width="180" show-overflow-tooltip />
        <el-table-column prop="subject" label="科目" width="100" />
        <el-table-column prop="score" label="分数" width="80" align="center">
          <template #default="{ row }">
            <span :style="{ color: getScoreColor(row.score), fontWeight: 600 }">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="passed" label="是否及格" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.passed ? 'success' : 'danger'" size="small">
              {{ row.passed ? '及格' : '不及格' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rank" label="排名" width="80" align="center">
          <template #default="{ row }">{{ row.rank ?? '-' }}</template>
        </el-table-column>
        <el-table-column prop="remarks" label="备注" show-overflow-tooltip />
        <el-table-column prop="created_at" label="录入时间" width="160" align="center">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openDialog('edit', row)">
              <el-icon><Edit /></el-icon> 编辑
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

    <!-- 录入/编辑成绩弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '录入成绩' : '编辑成绩'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="学员" prop="student_id">
          <el-select v-model="form.student_id" placeholder="请选择学员" filterable style="width: 100%" :disabled="dialogType === 'edit'">
            <el-option v-for="s in studentOptions" :key="s.id" :label="`${s.name} (ID: ${s.id})`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试" prop="exam_id">
          <el-select v-model="form.exam_id" placeholder="请选择考试" filterable style="width: 100%" :disabled="dialogType === 'edit'">
            <el-option v-for="e in examOptions" :key="e.id" :label="`${e.name} (${e.subject})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分数" prop="score">
          <el-input-number v-model="form.score" :min="0" :max="999" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排名" prop="rank">
          <el-input-number v-model="form.rank" :min="1" :max="9999" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="form.remarks" type="textarea" :rows="2" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确认</el-button>
      </template>
    </el-dialog>

    <!-- 批量录入弹窗 -->
    <el-dialog v-model="batchDialogVisible" title="批量录入成绩" width="700px" destroy-on-close>
      <el-alert type="info" :closable="false" style="margin-bottom: 16px">
        请为每个学员选择考试并输入分数，系统会自动判断是否及格
      </el-alert>
      <div v-for="(item, index) in batchForm" :key="index" style="margin-bottom: 12px; display: flex; gap: 8px; align-items: center;">
        <el-select v-model="item.student_id" placeholder="选择学员" filterable style="width: 200px">
          <el-option v-for="s in studentOptions" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="item.exam_id" placeholder="选择考试" filterable style="width: 220px">
          <el-option v-for="e in examOptions" :key="e.id" :label="e.name" :value="e.id" />
        </el-select>
        <el-input-number v-model="item.score" :min="0" :max="999" :precision="1" placeholder="分数" style="width: 120px" />
        <el-button type="danger" :icon="Delete" circle size="small" @click="batchForm.splice(index, 1)" />
      </div>
      <el-button type="primary" :icon="Plus" @click="batchForm.push({ student_id: null, exam_id: null, score: 0 })" style="margin-top: 8px">
        添加一行
      </el-button>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchSubmit" :loading="batchLoading">确认批量录入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getScores, createScore, updateScore, deleteScore, batchCreateScores } from '../api/scores'
import { getStudents } from '../api/students'
import { getExams } from '../api/exams'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Refresh, Plus, Upload, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const submitLoading = ref(false)
const batchLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const batchDialogVisible = ref(false)
const dialogType = ref('add')
const currentRow = ref(null)
const formRef = ref(null)
const studentOptions = ref([])
const examOptions = ref([])

const filters = reactive({ student_id: null, exam_id: null, passed: null })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const form = reactive({ student_id: null, exam_id: null, score: 0, rank: null, remarks: '' })
const batchForm = ref([{ student_id: null, exam_id: null, score: 0 }])

const formRules = {
  student_id: [{ required: true, message: '请选择学员', trigger: 'change' }],
  exam_id: [{ required: true, message: '请选择考试', trigger: 'change' }],
  score: [{ required: true, message: '请输入分数', trigger: 'blur' }],
}

const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.pageSize }
    if (filters.student_id) params.student_id = filters.student_id
    if (filters.exam_id) params.exam_id = filters.exam_id
    if (filters.passed !== null && filters.passed !== '') params.passed = filters.passed

    const res = await getScores(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    console.error('加载成绩数据失败:', e)
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [studentsRes, examsRes] = await Promise.all([
      getStudents({ page: 1, page_size: 100 }),
      getExams({ page: 1, page_size: 100 }),
    ])
    studentOptions.value = studentsRes.items || []
    examOptions.value = examsRes.items || []
  } catch (e) {
    console.error('加载选项数据失败:', e)
  }
}

const handleSearch = () => { pagination.page = 1; loadData() }
const resetFilters = () => {
  Object.assign(filters, { student_id: null, exam_id: null, passed: null })
  pagination.page = 1
  loadData()
}

const openDialog = (type, row = null) => {
  dialogType.value = type
  if (type === 'add') {
    Object.assign(form, { student_id: null, exam_id: null, score: 0, rank: null, remarks: '' })
  } else {
    Object.assign(form, {
      student_id: row.student_id, exam_id: row.exam_id,
      score: row.score, rank: row.rank, remarks: row.remarks,
    })
    currentRow.value = row
  }
  dialogVisible.value = true
}

const openBatchDialog = () => {
  batchForm.value = [{ student_id: null, exam_id: null, score: 0 }]
  batchDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      if (dialogType.value === 'add') {
        await createScore({ ...form })
        ElMessage.success('成绩录入成功')
      } else {
        await updateScore(currentRow.value.id, { score: form.score, rank: form.rank, remarks: form.remarks })
        ElMessage.success('成绩更新成功')
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

const handleBatchSubmit = async () => {
  const validItems = batchForm.value.filter(item => item.student_id && item.exam_id)
  if (validItems.length === 0) {
    ElMessage.warning('请至少填写一条有效的成绩记录')
    return
  }
  batchLoading.value = true
  try {
    const res = await batchCreateScores(validItems)
    ElMessage.success(res.message || '批量录入完成')
    batchDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error('批量录入失败:', e)
  } finally {
    batchLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.student_name}」在「${row.exam_name}」的成绩记录吗？`, '删除确认', {
      confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning',
    })
    await deleteScore(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch { /* 取消 */ }
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>

<style scoped>
.scores-container { min-height: 100%; }
.filter-card { border-radius: 12px; }
.filter-form { display: flex; flex-wrap: wrap; align-items: center; }
.action-bar { margin-top: 12px; display: flex; gap: 8px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
