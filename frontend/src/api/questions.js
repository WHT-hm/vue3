import request from './index'

// 获取题目列表
export function getQuestions(params) {
  return request.get('/api/questions', { params })
}

// 获取题目详情
export function getQuestion(id) {
  return request.get(`/api/questions/${id}`)
}

// 创建题目
export function createQuestion(data) {
  return request.post('/api/questions', data)
}

// 更新题目
export function updateQuestion(id, data) {
  return request.put(`/api/questions/${id}`, data)
}

// 删除题目
export function deleteQuestion(id) {
  return request.delete(`/api/questions/${id}`)
}

// 批量创建题目
export function batchCreateQuestions(data) {
  return request.post('/api/questions/batch', data)
}

// 从JSON文件导入题目
export function importQuestionsFromFile(examId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/api/questions/import?exam_id=${examId}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 清空考试的所有题目
export function clearExamQuestions(examId) {
  return request.delete(`/api/questions/exam/${examId}`)
}

// 执行代码并测试
export function executeCode(data) {
  return request.post('/api/questions/execute', data)
}
