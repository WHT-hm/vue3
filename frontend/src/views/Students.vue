<template>
  <div class="students-container">
    <!-- 搜索和操作区 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="filters.keyword"
            placeholder="姓名/电话/学号"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="在读" value="active" />
            <el-option label="休学" value="inactive" />
            <el-option label="毕业" value="graduated" />
          </el-select>
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="filters.school" placeholder="学校名称" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="resetFilters" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
      <div class="action-bar">
        <el-button type="primary" @click="openDialog('add')" :icon="Plus">新增学员</el-button>
        <el-button type="success" @click="loadData" :icon="Refresh">刷新</el-button>
      </div>
    </el-card>

    <!-- 学员列表 -->
    <el-card shadow="hover" style="margin-top: 16px; border-radius: 12px">
      <el-table :data="tableData" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="school" label="学校" show-overflow-tooltip />
        <el-table-column prop="major" label="专业" show-overflow-tooltip />
        <el-table-column prop="student_no" label="学号" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.student_no">{{ row.student_no }}</span>
            <span v-else style="color: #c0c4cc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_registered" label="注册状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_registered" type="success" size="small">已注册</el-tag>
            <el-tag v-else type="info" size="small">未注册</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type || 'info'" size="small">
              {{ statusMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score_count" label="考试次数" width="90" align="center" />
        <el-table-column prop="avg_score" label="平均分" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.avg_score != null" :style="{ color: row.avg_score >= 60 ? '#67c23a' : '#f56c6c' }">
              {{ row.avg_score }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.pass_rate != null">{{ row.pass_rate }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
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

      <!-- 分页 -->
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
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增学员' : '编辑学员'"
      width="600px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="form.gender">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="form.age" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学号" prop="id_card">
              <el-input v-model="form.id_card" placeholder="请输入学号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学校" prop="school">
              <el-input v-model="form.school" placeholder="请输入学校/单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业" prop="major">
              <el-input v-model="form.major" placeholder="请输入专业" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="报名日期" prop="enrollment_date">
              <el-date-picker v-model="form.enrollment_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" style="width: 100%">
                <el-option label="在读" value="active" />
                <el-option label="休学" value="inactive" />
                <el-option label="毕业" value="graduated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ dialogType === 'add' ? '确认添加' : '确认修改' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="学员详情" width="550px">
      <el-descriptions :column="2" border v-if="currentRow">
        <el-descriptions-item label="ID">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ currentRow.gender }}</el-descriptions-item>
        <el-descriptions-item label="年龄">{{ currentRow.age || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentRow.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentRow.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="学号">{{ currentRow.id_card || '-' }}</el-descriptions-item>
        <el-descriptions-item label="学校">{{ currentRow.school || '-' }}</el-descriptions-item>
        <el-descriptions-item label="专业">{{ currentRow.major || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusMap[currentRow.status]?.type || 'info'" size="small">
            {{ statusMap[currentRow.status]?.label || currentRow.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="考试次数">{{ currentRow.score_count }}</el-descriptions-item>
        <el-descriptions-item label="平均分">{{ currentRow.avg_score ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="通过率">{{ currentRow.pass_rate != null ? currentRow.pass_rate + '%' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="报名日期">{{ currentRow.enrollment_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentRow.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getStudents, createStudent, updateStudent, deleteStudent } from '../api/students'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Refresh, Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const dialogType = ref('add')
const currentRow = ref(null)
const formRef = ref(null)

const statusMap = {
  active: { label: '在读', type: 'success' },
  inactive: { label: '休学', type: 'warning' },
  graduated: { label: '毕业', type: 'info' },
}

const filters = reactive({
  keyword: '',
  status: '',
  school: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const form = reactive({
  name: '',
  gender: '男',
  age: null,
  phone: '',
  email: '',
  id_card: '',
  school: '',
  major: '',
  enrollment_date: '',
  status: 'active',
  remark: '',
})

const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
}

const resetForm = () => {
  Object.assign(form, {
    name: '',
    gender: '男',
    age: null,
    phone: '',
    email: '',
    id_card: '',
    school: '',
    major: '',
    enrollment_date: '',
    status: 'active',
    remark: '',
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.status) params.status = filters.status
    if (filters.school) params.school = filters.school

    const res = await getStudents(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (e) {
    console.error('加载学员数据失败:', e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.school = ''
  pagination.page = 1
  loadData()
}

const openDialog = (type, row = null) => {
  dialogType.value = type
  if (type === 'add') {
    resetForm()
  } else {
    Object.assign(form, {
      name: row.name,
      gender: row.gender,
      age: row.age,
      phone: row.phone,
      email: row.email,
      id_card: row.id_card,
      school: row.school,
      major: row.major,
      enrollment_date: row.enrollment_date,
      status: row.status,
      remark: row.remark,
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
        await createStudent({ ...form })
        ElMessage.success('学员添加成功')
      } else {
        await updateStudent(currentRow.value.id, { ...form })
        ElMessage.success('学员信息更新成功')
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
    await ElMessageBox.confirm(`确定删除学员「${row.name}」吗？删除后不可恢复！`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteStudent(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
    // 取消删除
  }
}

const viewDetail = (row) => {
  currentRow.value = row
  detailVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.students-container {
  min-height: 100%;
}

.filter-card {
  border-radius: 12px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.action-bar {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
