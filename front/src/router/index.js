import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/components/home/HomePage.vue'
import Editor from '@/components/editor/EditorPage.vue'
import New from '@/components/new/NewPage.vue'
import NewPrompt from '@/components/new/NewPromptPage.vue'
import Reset from '@/components/reset/ResetPage.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/editor/:type?', name: 'editor', component: Editor },
    { path: '/new', name: 'new', component: New},
    { path: '/new-prompt', name: 'newPrompt', component: NewPrompt},
    { path: '/reset', name: 'reset', component: Reset}
    // { path: '/:pathMatch(.*)*', name: '404', component: Page404  }
  ]
})

export default router
