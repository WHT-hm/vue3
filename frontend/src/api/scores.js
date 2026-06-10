import request from './index'

// 获取成绩列表
export function getScores(params) {
  return request.get('/api/scores', { params })
}

// 获取成绩详情
export function getScore(id) {
  return request.get(`/api/scores/${id}`)
}

// 录入成绩
export function createScore(data) {
  return request.post('/api/scores', data)
}

// 批量录入成绩
export function batchCreateScores(data) {
  return request.post('/api/scores/batch', data)
}

// 更新成绩
export function updateScore(id, data) {
  return request.put(`/api/scores/${id}`, data)
}

// 删除成绩
export function deleteScore(id) {
  return request.delete(`/api/scores/${id}`)
}

// 获取学员成绩历史
export function getStudentScoreHistory(studentId) {
  return request.get(`/api/scores/student/${studentId}/history`)
}
