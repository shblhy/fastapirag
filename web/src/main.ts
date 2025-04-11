import { createApp } from 'vue'
// import Vue from 'vue'
import './style.css'
import App from './App.vue'
import router from "./router/index";
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './utils/axios'  // 引入 axios 配置
import { useUserStore } from './stores/user'

const app = createApp(App)
const pinia = createPinia()

app.use(router)
   .use(pinia)
   .use(ElementPlus)

const userStore = useUserStore()
userStore.init().then(() => {
  app.mount('#app')
}).catch(error => {
  console.error('Failed to initialize user store:', error)
  app.mount('#app') // 即使初始化失败也挂载应用
})


