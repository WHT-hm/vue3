import request from './index'

// 用户登录
export function login(data) {
  return request.post('/api/auth/login', data)
}

// 用户登出
export function logout() {
  return request.post('/api/auth/logout')
}

// 获取当前用户信息
export function getMe() {
  return request.get('/api/auth/me')
}

// 修改密码
export function changePassword(data) {
  return request.put('/api/auth/change-password', data)
}
