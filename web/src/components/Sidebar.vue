<template>
  <div class="sidebar">
    <div class="header">
      <div class="user-info">
        <el-avatar :size="32" :src="userAvatar" />
        <div class="user-meta">
          <span class="username">{{ userStore.username }}</span>
          <el-button type="text" size="small" @click="handleLogout" class="logout-btn">
            退出登录
          </el-button>
        </div>
      </div>
      <el-button-group>
        <el-button type="primary" @click="startNewChat">
          <el-icon><Plus /></el-icon>
          新对话
        </el-button>
      </el-button-group>
    </div>
    
    <div class="chat-list">
      <div v-for="chat in chatList" 
           :key="chat.id"
           class="chat-item"
           :class="{ active: chat.id === currentChatId }"
           @click="selectChat(chat.id)">
        <el-icon><ChatDotRound /></el-icon>
        <span class="title">{{ chat.title }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/user'
import { useChatStore } from '../stores/chat'
import { Plus, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

interface Chat {
  id: string
  title: string
  messages: any[]
}

const router = useRouter()
const userStore = useUserStore()
const chatStore = useChatStore()
const currentChatId = ref<string | null>(null)
const userAvatar = 'https://bangkecs.oss-cn-hangzhou.aliyuncs.com/img%2Faflufzkgnvbatf346ucziw.png?OSSAccessKeyId=LTAI5tB5XRKP2jNcCyMrq1jo&Expires=96331954954&Signature=XNxYiVNZeCP5GOeuCNAuR74u9gw%3D'

const startNewChat = () => {
  const chatId = chatStore.createNewChat()
  currentChatId.value = chatId
}

const selectChat = (chatId: string) => {
  currentChatId.value = chatId
}

const chatList = computed(() => chatStore.chatList as Chat[])

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    try {
      // 调用后端登出接口
      await fetch('/users/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      
      // 清除 token
      localStorage.removeItem('token')
      // 清除用户状态
      userStore.$reset()
      // 清除聊天状态
      chatStore.$reset()
      // 跳转到登录页
      router.push('/login')
      
    } catch (error) {
      console.error('登出失败:', error)
      // 即使后端请求失败，也清除本地状态并跳转
      localStorage.removeItem('token')
      userStore.$reset()
      chatStore.$reset()
      router.push('/login')
    }
  } catch {
    // 用户取消操作
  }
}
</script>

<style lang="scss" scoped>
.sidebar {
  height: 100vh;
  width: 260px;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  
  .header {
    padding: 12px;
    border-bottom: 1px solid #e6e6e6;
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      
      .user-meta {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      
      .username {
        font-size: 14px;
        color: #333;
      }
      
      .logout-btn {
        padding: 0;
        height: auto;
        font-size: 12px;
        color: #909399;
        
        &:hover {
          color: #409eff;
        }
      }
    }
  }
  
  .chat-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    
    .chat-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 6px;
      cursor: pointer;
      
      &:hover {
        background-color: #f5f7fa;
      }
      
      &.active {
        background-color: #ecf5ff;
        color: #409eff;
      }
      
      .title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
</style> 