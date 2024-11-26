import { createRouter, createWebHistory } from 'vue-router'
import SearchView from '../views/search/SearchView.vue'
import TrendsView from '../views/trends/TrendsView.vue'
import HelpView from '../views/help/HelpView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: SearchView,
    },
    {
      path: '/trends',
      component: TrendsView,
    },
    {
      path: '/uitleg',
      component: HelpView,
    },
  ]
})

export default router
