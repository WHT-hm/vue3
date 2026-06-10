import request from './index'

// 注册
export function register(data) {
  return request.post('/api/student/register', data)
}

// 登录
export function login(data) {
  return request.post('/api/student/login', data)
}

// 登出
export function logout() {
  return request.post('/api/student/logout')
}

// 获取当前学员信息
export function getMe() {
  return request.get('/api/student/me')
}

// 获取考试列表
export function getExams() {
  return request.get('/api/student/exams')
}

// 获取考试题目
export function getExamQuestions(examId) {
  return request.get(`/api/student/exams/${examId}/questions`)
}

// 提交答案
export function submitExam(examId, data) {
  return request.post(`/api/student/exams/${examId}/submit`, data)
}

// 获取考试结果
// 获取考试结果
export function getExamResult(examId) {
  return request.get(`/api/student/exams/${examId}/result`)
}

// 查询考试状态
export function checkExamStatus(examId) {
  return request.get(`/api/student/exams/${examId}/status`)
}

// 运行代码测试
export function runCode(data) {
  return request.post('/api/student/run-code', data)
}
