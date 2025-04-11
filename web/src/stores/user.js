import { defineStore } from 'pinia'
import axios from 'axios'
import router from '../router'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token'),
    userInfo: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    username: (state) => state.userInfo?.username,
    avatar: (state) => state.userInfo?.avatar || '/default-avatar.png'
  },
  
  actions: {
    async init() {
      // 初始化时检查 token 并获取用户信息
      if (this.token) {
        try {
          await this.fetchUserInfo()
        } catch (error) {
          // token 无效或过期
          this.logout()
          router.push('/login')
        }
      }
    },
    
    async login(username, password) {
      try {
        const formData = new URLSearchParams()
        formData.append('username', username)
        formData.append('password', password)
        
        const response = await axios.post('/token', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
        
        this.token = response.data.access_token
        localStorage.setItem('token', this.token)
        
        await this.fetchUserInfo()
        return true
      } catch (error) {
        console.error('Login failed:', error)
        return false
      }
    },
    
    async fetchUserInfo() {
      try {
        const response = await axios.get('/users/me', {
          headers: {
            Authorization: `Bearer ${this.token}`
          }
        })
        this.userInfo = response.data
      } catch (error) {
        console.error('Failed to fetch user info:', error)
        throw error
      }
    },
    
    logout() {
      this.token = null
      this.userInfo = null
      localStorage.removeItem('token')
      router.push('/login')
    }
  }
}) 