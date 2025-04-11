import { defineStore } from 'pinia'
import config from '../config'

export const useChatStore = defineStore('chat', {
  state: () => ({
    chatList: [],
    currentChatId: null,
    isStreaming: false
  }),
  
  getters: {
    getCurrentChat: (state) => 
      state.chatList.find(chat => chat.id === state.currentChatId)
  },
  
  actions: {
    createNewChat() {
      const currentTime = new Date().toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      })
      
      const newChat = {
        id: Date.now().toString(),
        title: `新对话 ${currentTime}`,
        messages: []
      }
      
      this.chatList.unshift(newChat)
      this.currentChatId = newChat.id
      return newChat.id
    },

    async sendMessage(message) {
      const chat = this.getCurrentChat
      if (!chat) return
      
      // 添加用户消息
      chat.messages.push(message)
      
      // 创建助手消息占位
      const assistantMessage = {
        role: 'assistant',
        content: ''
      }
      chat.messages.push(assistantMessage)
      
      try {
        this.isStreaming = true
        // 构建 URL 参数
        const params = new URLSearchParams({
          prompt: message.content,
          with_his: true
        })

        // 使用 fetch API 代替 EventSource
        const response = await fetch(`${config.apiBaseUrl}/v1/chat/completions?${params}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
          }
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { value, done } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')
          
          for (const line of lines) {
            if (line.trim() === '') continue
            
            try {
              if (line.startsWith('data: ')) {
                const eventData = line.slice(6) // 移除 "data: " 前缀
                if (eventData.trim() === '[DONE]') {
                  // 收到结束标记，跳出循环
                  break
                } else {
                  try {
                    const parsedData = JSON.parse(eventData)
                    if (parsedData.data) {
                      assistantMessage.content += parsedData.data
                    }
                  } catch {
                    // 如果不是 JSON 且不是 [DONE]，才添加文本
                    if (eventData.trim() !== '[DONE]') {
                      assistantMessage.content += eventData
                    }
                  }
                }
              }
            } catch (e) {
              console.error('Error parsing SSE message:', e)
            }
          }
        }
        
      } catch (error) {
        console.error('Failed to get AI response:', error)
        assistantMessage.content = '消息发送失败，请重试'
      } finally {
        this.isStreaming = false
      }
    },

    async loadChatHistory() {
      try {
        const response = await fetch(`${config.apiBaseUrl}/v1/chat/history`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        
        if (data.history.length > 0) {
          const chatHistory = {
            id: 'history',
            title: '历史对话',
            messages: data.history.flat()
          }
          this.chatList = [chatHistory]
          this.currentChatId = 'history'
        } else {
          this.createNewChat()
        }
      } catch (error) {
        console.error('Failed to load chat history:', error)
        this.createNewChat()
      }
    }
  }
}) 

const userAvatar = 'https://bangkecs.oss-cn-hangzhou.aliyuncs.com/img%2Faflufzkgnvbatf346ucziw.png?OSSAccessKeyId=LTAI5tB5XRKP2jNcCyMrq1jo&Expires=96331954954&Signature=XNxYiVNZeCP5GOeuCNAuR74u9gw%3D'
const botAvatar = 'https://bangkesrc.oss-cn-hangzhou.aliyuncs.com/img%2F60996958-5469-11ef-bb64-74563c8eef74.webp?OSSAccessKeyId=LTAI5tB5XRKP2jNcCyMrq1jo&Expires=96331000976&Signature=pLx%2BIoDL4F%2FNKObuHWNh54CT4%2B0%3D' 