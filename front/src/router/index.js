import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/components/home/HomePage.vue'
import Editor from '@/components/editor/EditorPage.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/editor', name: 'editor', component: Editor },
    // { path: '/:pathMatch(.*)*', name: '404', component: Page404  }
  ]
})

export default router
