import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, logout as logoutApi, getMe } from '../api/student'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('student_token') || '')
  const student = ref(JSON.parse(localStorage.getItem('student_info') || 'null'))
  const isLoggedIn = ref(!!token.value)

  async function login(studentNo, password) {
    const res = await loginApi({ student_no: studentNo, password })
    token.value = res.token
    student.value = res.student
    isLoggedIn.value = true
    localStorage.setItem('student_token', res.token)
    localStorage.setItem('student_info', JSON.stringify(res.student))
    return res
  }

  async function logout() {
    try {
      await logoutApi()
    } catch (e) {
      // ignore
    }
    token.value = ''
    student.value = null
    isLoggedIn.value = false
    localStorage.removeItem('student_token')
    localStorage.removeItem('student_info')
  }

  async function fetchMe() {
    try {
      const res = await getMe()
      student.value = res.data
      localStorage.setItem('student_info', JSON.stringify(res.data))
    } catch (e) {
      // token invalid
      logout()
    }
  }

  return { token, student, isLoggedIn, login, logout, fetchMe }
})
