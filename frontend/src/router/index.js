import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import MeetingRoomView from '../views/MeetingRoomView.vue'
import CreditorsView from '../views/CreditorsView.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: LoginView },
  { path: '/dashboard', component: DashboardView },
  { path: '/meetings/:id', component: MeetingRoomView },
  { path: '/creditors', component: CreditorsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router