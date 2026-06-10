import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', noAuth: true },
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '考试统计' },
      },
      {
        path: 'students',
        name: 'Students',
        component: () => import('../views/Students.vue'),
        meta: { title: '学员管理' },
      },
      {
        path: 'exams',
        name: 'Exams',
        component: () => import('../views/Exams.vue'),
        meta: { title: '考试管理' },
      },
      {
        path: 'scores',
        name: 'Scores',
        component: () => import('../views/Scores.vue'),
        meta: { title: '成绩管理' },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/Users.vue'),
        meta: { title: '用户管理' },
      },
    ],
  },
  {
    path: '/code-runner/:id?',
    name: 'CodeRunner',
    component: () => import('../views/CodeRunner.vue'),
    meta: { title: '编程题', noAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 导航守卫 - 未登录跳转到登录页
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 考试学员管理系统` : '考试学员管理系统'

  const token = localStorage.getItem('token')
  if (to.meta.noAuth || token) {
    next()
  } else {
    next('/login')
  }
})

export default router
