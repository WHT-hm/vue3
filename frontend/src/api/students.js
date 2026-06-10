import request from './index'

// 获取学员列表
export function getStudents(params) {
  return request.get('/api/students', { params })
}

// 获取学员详情
export function getStudent(id) {
  return request.get(`/api/students/${id}`)
}

// 创建学员
export function createStudent(data) {
  return request.post('/api/students', data)
}

// 更新学员
export function updateStudent(id, data) {
  return request.put(`/api/students/${id}`, data)
}

// 删除学员
export function deleteStudent(id) {
  return request.delete(`/api/students/${id}`)
}
