import { createRouter, createWebHistory } from 'vue-router'
import SearchView from '../views/SearchView.vue'
import TrendsView from '../views/TrendsView.vue'
import HelpView from '../views/HelpView.vue'
import HomeView from '../views/HomeView.vue'
import AboutView from '../views/AboutView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: HomeView,
    },
    {
      path: '/trends',
      name: 'trends',
      component: TrendsView,
    },
    {
      path: '/help',
      component: HelpView,
    },
    {
      path: '/grafiek',
      component: SearchView,
    },
    {
      path: '/over',
      component: AboutView,
    },
  ]
})

export default router
