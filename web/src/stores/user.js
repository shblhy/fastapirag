import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import config from '../config'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: '',
    isAuthenticated: false
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    avatar: (state) => state.userInfo?.avatar || '/default-avatar.png'
  },
  
  actions: {
    async login(username, password) {
      try {
        const formData = new URLSearchParams()
        formData.append('username', username)
        formData.append('password', password)

        const response = await fetch(`${config.apiBaseUrl}/token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: formData
        })

        if (!response.ok) {
          throw new Error('Login failed')
        }

        const data = await response.json()
        this.token = data.access_token
        this.username = username
        this.isAuthenticated = true
        localStorage.setItem('token', data.access_token)
        return true
      } catch (error) {
        console.error('Login error:', error)
        return false
      }
    },
    
    async init() {
      if (!this.token) return

      try {
        const response = await fetch(`${config.apiBaseUrl}/users/me`, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        if (!response.ok) {
          throw new Error('Failed to get user info')
        }

        const data = await response.json()
        this.username = data.username
        this.isAuthenticated = true
      } catch (error) {
        console.error('Init error:', error)
        this.logout()
      }
    },
    
    async logout() {
      try {
        const response = await fetch(`${config.apiBaseUrl}/users/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })

        if (!response.ok) {
          console.error('Logout failed on server')
        }
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.token = ''
        this.username = ''
        this.isAuthenticated = false
        localStorage.removeItem('token')
      }
    }
  }
}) 