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

// 初始化用户状态
const userStore = useUserStore()
await userStore.init()

app.mount('#app')


