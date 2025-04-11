import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'
import Chat from '../views/Chat.vue'
import Login from '../views/Login.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: Chat,
    meta: { requiresAuth: true }  // 需要认证
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }  // 游客可访问
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 检查用户是否已登录
  const isLoggedIn = userStore.isLoggedIn
  
  // 如果路由需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }  // 保存原目标路径
      })
    } else {
      next()
    }
  } 
  // 如果是游客页面（如登录页）
  else if (to.matched.some(record => record.meta.guest)) {
    if (isLoggedIn) {
      // 已登录用户访问登录页，重定向到首页
      next({ path: '/' })
    } else {
      next()
    }
  } 
  else {
    next()
  }
})

export default router 