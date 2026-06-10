<template>
  <div class="dashboard-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">学员总数</p>
              <h2 class="stat-value">{{ overview.total_students }}</h2>
              <p class="stat-desc">活跃: {{ overview.active_students }}</p>
            </div>
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea, #764ba2)">
              <el-icon :size="32"><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">考试总数</p>
              <h2 class="stat-value">{{ overview.total_exams }}</h2>
              <p class="stat-desc">即将开始: {{ overview.upcoming_exams }}</p>
            </div>
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb, #f5576c)">
              <el-icon :size="32"><Document /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">成绩记录</p>
              <h2 class="stat-value">{{ overview.total_scores }}</h2>
              <p class="stat-desc">总录入次数</p>
            </div>
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe, #00f2fe)">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">总体通过率</p>
              <h2 class="stat-value">{{ overview.overall_pass_rate ?? '-' }}<span v-if="overview.overall_pass_rate != null">%</span></h2>
              <p class="stat-desc">平均分: {{ overview.overall_avg_score ?? '-' }}</p>
            </div>
            <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b, #38f9d7)">
              <el-icon :size="32"><CircleCheck /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：学员排名 + 科目统计 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Trophy /></el-icon> 学员成绩排名 TOP 10</span>
            </div>
          </template>
          <el-table :data="rankings" stripe style="width: 100%" max-height="400">
            <el-table-column type="index" label="排名" width="70" align="center">
              <template #default="{ $index }">
                <el-tag
                  v-if="$index < 3"
                  :type="$index === 0 ? 'danger' : $index === 1 ? 'warning' : 'success'"
                  size="small"
                  round
                >
                  {{ $index + 1 }}
                </el-tag>
                <span v-else>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="student_name" label="姓名" width="100" />
            <el-table-column prop="school" label="学校" show-overflow-tooltip />
            <el-table-column prop="avg_score" label="平均分" width="90" align="center">
              <template #default="{ row }">
                <span :style="{ color: row.avg_score >= 60 ? '#67c23a' : '#f56c6c' }">
                  {{ row.avg_score }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="total_exams" label="考试数" width="80" align="center" />
            <el-table-column prop="pass_count" label="通过数" width="80" align="center" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><PieChart /></el-icon> 科目统计</span>
            </div>
          </template>
          <el-table :data="subjectStats" stripe style="width: 100%" max-height="400">
            <el-table-column prop="subject" label="科目" width="120" />
            <el-table-column prop="exam_count" label="考试数" width="80" align="center" />
            <el-table-column prop="avg_score" label="平均分" width="90" align="center">
              <template #default="{ row }">
                {{ row.avg_score ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="pass_rate" label="通过率" width="90" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.pass_rate || 0"
                  :stroke-width="6"
                  :color="row.pass_rate >= 60 ? '#67c23a' : '#f56c6c'"
                />
              </template>
            </el-table-column>
            <el-table-column prop="highest_score" label="最高分" width="80" align="center">
              <template #default="{ row }">
                {{ row.highest_score ?? '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="lowest_score" label="最低分" width="80" align="center">
              <template #default="{ row }">
                {{ row.lowest_score ?? '-' }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行：最近活动 + 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Bell /></el-icon> 最近活动</span>
            </div>
          </template>
          <el-timeline v-if="activities.length > 0">
            <el-timeline-item
              v-for="(item, index) in activities"
              :key="index"
              :timestamp="item.time"
              placement="top"
              :type="getActivityType(item.type)"
            >
              <el-tag :type="getActivityType(item.type)" size="small">{{ getActivityLabel(item.type) }}</el-tag>
              {{ item.description }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无活动记录" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="table-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Operation /></el-icon> 快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="$router.push('/students')">
              <el-icon><Plus /></el-icon> 添加学员
            </el-button>
            <el-button type="success" size="large" @click="$router.push('/exams')">
              <el-icon><Plus /></el-icon> 创建考试
            </el-button>
            <el-button type="warning" size="large" @click="$router.push('/scores')">
              <el-icon><Edit /></el-icon> 录入成绩
            </el-button>
            <el-button type="info" size="large" @click="refreshData">
              <el-icon><Refresh /></el-icon> 刷新数据
            </el-button>
          </div>
        </el-card>

        <el-card shadow="hover" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span><el-icon><Clock /></el-icon> 即将开始的考试</span>
            </div>
          </template>
          <div v-if="upcomingExams.length > 0">
            <div v-for="exam in upcomingExams" :key="exam.id" class="upcoming-exam-item">
              <div class="exam-name">{{ exam.name }}</div>
              <div class="exam-meta">
                <el-tag size="small" type="warning">{{ exam.subject }}</el-tag>
                <span class="exam-date">{{ formatDate(exam.exam_date) }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无即将开始的考试" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getOverview, getStudentRanking, getSubjectStats, getRecentActivities } from '../api/dashboard'
import { getUpcomingExams } from '../api/exams'

const overview = ref({})
const rankings = ref([])
const subjectStats = ref([])
const activities = ref([])
const upcomingExams = ref([])

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}
const getActivityType = (type) => {
  const map = { 'student_created': 'success', 'exam_created': 'warning', 'score_added': 'primary' }
  return map[type] || 'info'
}

const getActivityLabel = (type) => {
  const map = { 'student_created': '新增学员', 'exam_created': '新增考试', 'score_added': '成绩录入' }
  return map[type] || type
}

const loadData = async () => {
  try {
    const [overviewData, rankingData, subjectData, activityData, upcomingData] = await Promise.allSettled([
      getOverview(),
      getStudentRanking({ limit: 10 }),
      getSubjectStats(),
      getRecentActivities({ limit: 8 }),
      getUpcomingExams({ limit: 5 }),
    ])

    if (overviewData.status === 'fulfilled') overview.value = overviewData.value
    if (rankingData.status === 'fulfilled') rankings.value = rankingData.value.data || []
    if (subjectData.status === 'fulfilled') subjectStats.value = subjectData.value.data || []
    if (activityData.status === 'fulfilled') activities.value = activityData.value.data || []
    if (upcomingData.status === 'fulfilled') upcomingExams.value = upcomingData.value.data || []
  } catch (e) {
    console.error('加载考试统计数据失败:', e)
  }
}

const refreshData = () => {
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100%;
}

.stat-card {
  border-radius: 12px;
  border: none;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 4px 0;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
  margin: 0;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.table-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
}

.card-header span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-actions .el-button {
  width: 100%;
  height: 50px;
  border-radius: 10px;
}

.upcoming-exam-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.upcoming-exam-item:last-child {
  border-bottom: none;
}

.exam-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.exam-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.exam-date {
  font-size: 12px;
  color: #909399;
}
</style>
