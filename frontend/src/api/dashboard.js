import request from './index'

// 获取考试统计概览
export function getOverview() {
  return request.get('/api/dashboard/overview')
}

// 获取科目统计
export function getSubjectStats() {
  return request.get('/api/dashboard/subject-stats')
}

// 获取考试成绩分布
export function getExamScoreDistribution(examId) {
  return request.get(`/api/dashboard/score-distribution/${examId}`)
}

// 获取学员排名
export function getStudentRanking(params) {
  return request.get('/api/dashboard/student-ranking', { params })
}

// 获取月度趋势
export function getMonthlyTrend() {
  return request.get('/api/dashboard/monthly-trend')
}

// 获取最近活动
export function getRecentActivities(params) {
  return request.get('/api/dashboard/recent-activities', { params })
}
