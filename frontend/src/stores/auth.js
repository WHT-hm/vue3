import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getMe } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(!!localStorage.getItem('token'))
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const username = computed(() => userInfo.value?.real_name || userInfo.value?.username || '')
  const role = computed(() => userInfo.value?.role || '')
  const isSuperAdmin = computed(() => userInfo.value?.role === 'super_admin')

  async function login(user, password) {
    try {
      const res = await loginApi({ username: user, password })
      token.value = res.token
      userInfo.value = res.user
      isLoggedIn.value = true
      localStorage.setItem('token', res.token)
      localStorage.setItem('isLoggedIn', 'true')
      localStorage.setItem('userInfo', JSON.stringify(res.user))
      return true
    } catch (e) {
      return false
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } catch { /* 忽略 */ }
    isLoggedIn.value = false
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('userInfo')
  }

  async function fetchUserInfo() {
    try {
      const res = await getMe()
      userInfo.value = res
      localStorage.setItem('userInfo', JSON.stringify(res))
    } catch {
      // token 无效，清除登录状态
      isLoggedIn.value = false
      token.value = ''
      userInfo.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('isLoggedIn')
      localStorage.removeItem('userInfo')
    }
  }

  return { isLoggedIn, token, userInfo, username, role, isSuperAdmin, login, logout, fetchUserInfo }
})
