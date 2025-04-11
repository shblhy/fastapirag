import axios from 'axios'

// 配置基础URL
axios.defaults.baseURL = 'http://localhost:8798'  // 根据您的后端服务地址调整

// 请求拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 422:
          console.error('请求参数错误:', error.response.data)
          break
        case 401:
          // 未授权，清除 token 并跳转到登录页
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
      }
    }
    return Promise.reject(error)
  }
)

export default axios 