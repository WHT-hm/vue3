import request from './index'

// 获取用户列表
export function getUsers(params) {
  return request.get('/api/users', { params })
}

// 创建用户
export function createUser(data) {
  return request.post('/api/users', data)
}

// 更新用户
export function updateUser(id, data) {
  return request.put(`/api/users/${id}`, data)
}

// 删除用户
export function deleteUser(id) {
  return request.delete(`/api/users/${id}`)
}

// 重置用户密码
export function resetUserPassword(id, data) {
  return request.put(`/api/users/${id}/reset-password`, data)
}

// 切换用户状态（启用/禁用）
export function toggleUserStatus(id) {
  return request.put(`/api/users/${id}/toggle-status`)
}
