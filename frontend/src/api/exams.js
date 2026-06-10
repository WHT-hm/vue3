import request from './index'

// 获取考试列表
export function getExams(params) {
  return request.get('/api/exams', { params })
}

// 获取即将开始的考试
export function getUpcomingExams(params) {
  return request.get('/api/exams/upcoming', { params })
}

// 获取考试详情
export function getExam(id) {
  return request.get(`/api/exams/${id}`)
}

// 创建考试
export function createExam(data) {
  return request.post('/api/exams', data)
}

// 更新考试
export function updateExam(id, data) {
  return request.put(`/api/exams/${id}`, data)
}

// 删除考试
export function deleteExam(id) {
  return request.delete(`/api/exams/${id}`)
}

// 开始考试
export function startExam(id) {
  return request.post(`/api/exams/${id}/start`)
}

// 结束考试
export function endExam(id) {
  return request.post(`/api/exams/${id}/end`)
}

// 强制结束考试（修改题目后）
export function forceEndExam(id) {
  return request.post(`/api/exams/${id}/force-end`)
}

// 重新考试
export function retakeExam(id) {
  return request.post(`/api/exams/${id}/retake`)
}

// 导出考试人员
export function exportParticipants(examId) {
  return request.get('/api/exams/export/participants', {
    params: { exam_id: examId },
    responseType: 'blob'
  })
}

// 导出考试成绩
export function exportScores(examId) {
  return request.get('/api/exams/export/scores', {
    params: { exam_id: examId },
    responseType: 'blob'
  })
}

// 导出考试数据（人员+成绩）
export function exportAll(examId) {
  return request.get('/api/exams/export/all', {
    params: { exam_id: examId },
    responseType: 'blob'
  })
}
