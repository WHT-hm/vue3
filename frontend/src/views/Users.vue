<template>
  <div class="users-container">
    <!-- 搜索和操作区 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="用户名/姓名" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部" clearable style="width: 140px">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
          <el-button @click="resetFilters" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
      <div class="action-bar">
        <el-button type="primary" @click="openDialog('add')" :icon="Plus">添加用户</el-button>
        <el-button type="success" @click="loadData" :icon="Refresh">刷新</el-button>
      </div>
    </el-card>

    <!-- 用户列表 -->
    <el-card shadow="hover" style="margin-top: 16px; border-radius: 12px">
      <el-table :data="tableData" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="120">
          <template #default="{ row }">{{ row.real_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="130">
          <template #default="{ row }">{{ row.phone || '-' }}</template>
        </el-table-column>
        <el-table-column prop="student_no" label="学号" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.student_no || '-' }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160" align="center">
          <template #default="{ row }">{{ formatDate(row.last_login) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" align="center">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openDialog('edit', row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button
              :type="row.status === 'active' ? 'warning' : 'success'"
              link size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button type="info" link size="small" @click="handleResetPassword(row)">
              <el-icon><Key /></el-icon> 重置密码
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

    <!-- 添加/编辑用户弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'add' ? '添加用户' : '编辑用户'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="formRules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="dialogType === 'edit'" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'add'" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码（至少4位）" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="学号" prop="student_no">
          <el-input v-model="form.student_no" placeholder="请输入学号" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="超级管理员" value="super_admin" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确认</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="resetPwdVisible" title="重置密码" width="400px" destroy-on-close>
      <el-form ref="resetPwdFormRef" :model="resetPwdForm" :rules="resetPwdRules" label-width="80px">
        <el-form-item label="用户">
          <span>{{ resetPwdTarget?.username }}</span>
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetPwdForm.new_password" type="password" placeholder="请输入新密码（至少4位）" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPwdVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPwdSubmit" :loading="resetPwdLoading">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getUsers, createUser, updateUser, deleteUser, resetUserPassword, toggleUserStatus } from '../api/users'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Refresh, Plus, Delete, Edit, Key } from '@element-plus/icons-vue'

const loading = ref(false)
const submitLoading = ref(false)
const resetPwdLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const resetPwdVisible = ref(false)
const dialogType = ref('add')
const currentRow = ref(null)
const resetPwdTarget = ref(null)
const formRef = ref(null)
const resetPwdFormRef = ref(null)

const filters = reactive({ keyword: '', role: null, status: null })
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const form = reactive({ username: '', password: '', real_name: '', phone: '', student_no: '', role: 'admin' })
const resetPwdForm = reactive({ new_password: '' })

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度2-50位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 4, message: '密码至少4位', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const roleOrder = { super_admin: 0, admin: 1, user: 2 }
const roleLabel = (role) => {
  const map = { super_admin: '超级管理员', admin: '管理员', user: '普通用户' }
  return map[role] || role
}
const roleTagType = (role) => {
  const map = { super_admin: 'danger', admin: 'primary', user: '' }
  return map[role] || 'info'
}

const resetPwdRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 4, message: '密码至少4位', trigger: 'blur' },
  ],
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
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.role) params.role = filters.role
    if (filters.status) params.status = filters.status

    const res = await getUsers(params)
    const items = res.items || []
    // 超级管理员和管理员置顶显示
    items.sort((a, b) => (roleOrder[a.role] ?? 9) - (roleOrder[b.role] ?? 9))
    tableData.value = items
    pagination.total = res.total || 0
  } catch (e) {
    console.error('加载用户数据失败:', e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { pagination.page = 1; loadData() }
const resetFilters = () => {
  Object.assign(filters, { keyword: '', role: null, status: null })
  pagination.page = 1
  loadData()
}

const openDialog = (type, row = null) => {
  dialogType.value = type
  if (type === 'add') {
    Object.assign(form, { username: '', password: '', real_name: '', phone: '', student_no: '', role: 'admin' })
  } else {
    Object.assign(form, {
      username: row.username,
      real_name: row.real_name || '',
      phone: row.phone || '',
      student_no: row.student_no || '',
      role: row.role,
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
        await createUser({ ...form })
        ElMessage.success('用户创建成功')
      } else {
        await updateUser(currentRow.value.id, {
          real_name: form.real_name,
          phone: form.phone,
          student_no: form.student_no,
          role: form.role,
        })
        ElMessage.success('用户更新成功')
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

const handleToggleStatus = async (row) => {
  const action = row.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户「${row.username}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await toggleUserStatus(row.id)
    ElMessage.success(`${action}成功`)
    loadData()
  } catch { /* 取消 */ }
}

const handleResetPassword = (row) => {
  resetPwdTarget.value = row
  resetPwdForm.new_password = ''
  resetPwdVisible.value = true
}

const handleResetPwdSubmit = async () => {
  if (!resetPwdFormRef.value) return
  await resetPwdFormRef.value.validate(async (valid) => {
    if (!valid) return
    resetPwdLoading.value = true
    try {
      await resetUserPassword(resetPwdTarget.value.id, { new_password: resetPwdForm.new_password })
      ElMessage.success('密码重置成功')
      resetPwdVisible.value = false
    } catch (e) {
      console.error('重置密码失败:', e)
    } finally {
      resetPwdLoading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.username}」吗？此操作不可恢复。`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch { /* 取消 */ }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.users-container { min-height: 100%; }
.filter-card { border-radius: 12px; }
.filter-form { display: flex; flex-wrap: wrap; align-items: center; }
.action-bar { margin-top: 12px; display: flex; gap: 8px; }
.pagination-wrap { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
