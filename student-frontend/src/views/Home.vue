<template>
  <div class="home-container">
    <div class="home-header">
      <h2>学员考试系统</h2>
      <div class="header-right">
        <span class="student-name">欢迎，{{ studentName }}</span>
        <el-button type="danger" text @click="handleLogout">退出登录</el-button>
      </div>
    </div>
    <div class="home-content">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="待做考试" name="pending">
          <div v-if="pendingExams.length === 0" class="empty-tip">
            <el-empty description="暂无待做考试" />
          </div>
          <div v-else class="exam-list">
            <el-card v-for="exam in pendingExams" :key="exam.id" class="exam-card" shadow="hover">
              <div class="exam-info">
                <h3>{{ exam.name }}</h3>
                <p>科目：{{ exam.subject }}</p>
                <p>考试时间：{{ formatTime(exam.exam_date) }}</p>
                <p>时长：{{ exam.duration }} 分钟</p>
                <p>总分：{{ exam.total_score }} 分</p>
              </div>
              <el-button type="primary" @click="startExam(exam.id)">开始答题</el-button>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="已完成考试" name="completed">
          <div v-if="completedExams.length === 0" class="empty-tip">
            <el-empty description="暂无已完成考试" />
          </div>
          <div v-else class="exam-list">
            <el-card v-for="exam in completedExams" :key="exam.id" class="exam-card" shadow="hover">
              <div class="exam-info">
                <h3>{{ exam.name }}</h3>
                <p>科目：{{ exam.subject }}</p>
                <p>考试时间：{{ formatTime(exam.exam_date) }}</p>
                <p>时长：{{ exam.duration }} 分钟</p>
                <p>总分：{{ exam.total_score }} 分</p>
              </div>
              <el-button type="success" @click="viewResult(exam.id)">查看成绩</el-button>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { getExams } from '../api/student'

const router = useRouter()
const authStore = useAuthStore()
const activeTab = ref('pending')
const pendingExams = ref([])
const completedExams = ref([])

const studentName = computed(() => authStore.student?.name || '学员')

onMounted(() => {
  loadExams()
})

async function loadExams() {
  try {
    const res = await getExams()
    pendingExams.value = res.data.pending
    completedExams.value = res.data.completed
  } catch (e) {
    // handled by interceptor
  }
}

function formatTime(dt) {
  if (!dt) return '-'
  return new Date(dt).toLocaleString('zh-CN')
}

function startExam(examId) {
  router.push(`/exam/${examId}`)
}

function viewResult(examId) {
  router.push(`/exam/${examId}/result`)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}
.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.home-header h2 {
  margin: 0;
  color: #303133;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.student-name {
  color: #606266;
  font-size: 14px;
}
.home-content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.exam-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}
.exam-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.exam-card :deep(.el-card__body) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.exam-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
}
.exam-info p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}
.empty-tip {
  padding: 40px 0;
}
</style>
