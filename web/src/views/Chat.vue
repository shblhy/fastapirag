<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="user-info">
      </div>
      <el-button-group>
        <el-button 
          type="primary" 
          plain
          @click="chatStore.createNewChat()">
          新对话
        </el-button>
        <el-button 
          type="primary" 
          plain
          @click="loadHistory">
          历史对话
        </el-button>
      </el-button-group>
    </div>

    <div class="chat-messages" ref="messagesContainer">
      <template v-if="currentChat">
        <div v-for="(message, index) in currentChat.messages" 
             :key="index" 
             class="message"
             :class="message.role">
          <div class="avatar">
            <el-avatar :size="40" :src="message.role === 'user' ? userAvatar : botAvatar" />
          </div>
          <div class="content">
            <div class="text" :class="{ 'streaming': chatStore.isStreaming && index === currentChat.messages.length - 1 }">
              <template v-if="message.role === 'assistant' && chatStore.isStreaming && index === currentChat.messages.length - 1">
                <span class="typing-text">{{ displayedText }}</span>
                <span class="cursor"></span>
              </template>
              <template v-else>
                {{ message.content }}
              </template>
            </div>
            <div class="timestamp" v-if="message.created_at">
              {{ message.created_at }}
            </div>
          </div>
        </div>
      </template>
      <div v-else class="empty-state">
        <el-empty description="开始新的对话" />
      </div>
    </div>
    
    <div class="chat-input">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="3"
        placeholder="请输入消息..."
        :disabled="chatStore.isStreaming"
        @keyup.enter.prevent="sendMessage"
      />
      <div class="actions">
        <el-button-group>
          <el-button 
            type="primary" 
            @click="sendMessage"
            :loading="chatStore.isStreaming"
            :disabled="chatStore.isStreaming || !currentChat">
            {{ chatStore.isStreaming ? '响应中...' : '发送' }}
          </el-button>
        </el-button-group>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch, watchEffect } from 'vue'
import { useUserStore } from '../stores/user'
import { useChatStore } from '../stores/chat'
import { fetchEventSource } from '@microsoft/fetch-event-source'

// 头像配置
const userAvatar = 'https://bangkecs.oss-cn-hangzhou.aliyuncs.com/img%2Faflufzkgnvbatf346ucziw.png?OSSAccessKeyId=LTAI5tB5XRKP2jNcCyMrq1jo&Expires=96331954954&Signature=XNxYiVNZeCP5GOeuCNAuR74u9gw%3D'
const botAvatar = 'https://bangkesrc.oss-cn-hangzhou.aliyuncs.com/img%2F60996958-5469-11ef-bb64-74563c8eef74.webp?OSSAccessKeyId=LTAI5tB5XRKP2jNcCyMrq1jo&Expires=96331000976&Signature=pLx%2BIoDL4F%2FNKObuHWNh54CT4%2B0%3D'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  created_at?: string
}

interface Chat {
  id: string
  title: string
  messages: ChatMessage[]
}

const userStore = useUserStore()
const chatStore = useChatStore()
const messagesContainer = ref<HTMLElement | null>(null)
const inputMessage = ref('')
const displayedText = ref('')
const typingSpeed = 50 // 打字速度（毫秒）

const currentChat = computed<Chat | undefined>(() => chatStore.getCurrentChat)

const sendMessage = async () => {
  if (!inputMessage.value.trim() || !currentChat.value) return
  
  const message = inputMessage.value
  inputMessage.value = ''
  displayedText.value = ''
  const currentTime = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })

  // 添加用户消息
  const userMessage: ChatMessage = {
    role: 'user' as const,
    content: message,
    created_at: currentTime
  }
  currentChat.value.messages.push(userMessage)
  
  // 添加助手消息占位
  const assistantMessage: ChatMessage = {
    role: 'assistant' as const,
    content: '',
    created_at: currentTime
  }
  currentChat.value.messages.push(assistantMessage)
  
  // 构建 URL 参数
  const params = new URLSearchParams({
    prompt: message,
    with_his: 'true'
  })

  try {
    chatStore.isStreaming = true
    const authorizationToken = localStorage.getItem('token')
    
    await fetchEventSource(`http://localhost:8798/v1/chat/completions?${params}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authorizationToken}`,
        'Accept': 'text/event-stream',
      },
      onmessage(event) {
        const time = new Date().toLocaleTimeString()
        if (event.data === '[DONE]') {
          console.log(`[${time}] 流式响应完成`)
          chatStore.isStreaming = false
          return
        }
        
        try {
          const data = event.data;

          if (data) {
            assistantMessage.content += data
            displayedText.value = assistantMessage.content
          }
        } catch (e) {
          console.error('解析消息失败:', e)
        }
      },
      onclose() {
        console.log('连接已关闭')
        chatStore.isStreaming = false
      },
      onerror(err) {
        console.error('发生错误:', err)
        chatStore.isStreaming = false
      }
    })
  } catch (error) {
    console.error('发送消息失败:', error)
    assistantMessage.content = '消息发送失败，请重试'
    chatStore.isStreaming = false
  }
  
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = messagesContainer.value
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

const loadHistory = async () => {
  await chatStore.loadChatHistory()
  scrollToBottom()
}

onMounted(async () => {
  if (!currentChat.value) {
    chatStore.createNewChat()
  }
  await loadHistory()
})

watch(
  () => currentChat.value?.messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)
</script>

<style lang="scss" scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  flex: 1;
  width: 100%;
  
  .chat-header {
    padding: 12px 20px;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #fff;
    width: 100%;

    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .user-avatar {
        border-radius: 50%;
        border: 2px solid #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .username {
        font-size: 16px;
        font-weight: 500;
        color: #333;
      }
    }
  }
  
  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background-color: #f9fafb;
    width: 100%;
    display: flex;
    flex-direction: column;
    
    .empty-state {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: calc(100vh - 180px);
    }
    
    .message {
      display: flex;
      margin-bottom: 20px;
      align-items: flex-start;
      width: 100%;
      
      &.user {
        flex-direction: row-reverse;
        
        .content {
          margin-right: 12px;
          margin-left: 0;
          
          .text {
            background-color: #ecf5ff;
            border: 1px solid #d9ecff;
          }
        }
      }
      
      &.assistant {
        .content {
          .text {
            background-color: #fff;
            border: 1px solid #e6e6e6;
          }
        }
      }
      
      .avatar {
        flex-shrink: 0;
      }
      
      .content {
        margin-left: 12px;
        max-width: 70%;
        
        .text {
          padding: 12px 16px;
          border-radius: 8px;
          font-size: 14px;
          line-height: 1.6;
          word-break: break-word;
          
          &.streaming {
            .cursor {
              display: inline-block;
              width: 2px;
              height: 15px;
              background-color: currentColor;
              margin-left: 2px;
              animation: blink 1s infinite;
            }

            .typing-text {
              white-space: pre-wrap;
              word-break: break-word;
            }
          }
        }
        
        .timestamp {
          font-size: 12px;
          color: #999;
          margin-top: 4px;
          padding: 0 4px;
        }
      }
    }
  }
  
  .chat-input {
    border-top: 1px solid #e6e6e6;
    padding: 20px;
    background-color: #fff;
    width: 100%;
    
    .el-textarea {
      width: 100%;
      
      .el-textarea__inner {
        resize: none;
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        width: 100%;
        
        &:focus {
          border-color: #409eff;
        }
      }
    }
    
    .actions {
      margin-top: 12px;
      display: flex;
      justify-content: flex-end;
      width: 100%;
      
      .el-button {
        padding: 8px 24px;
        font-size: 14px;
      }
    }
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style> 