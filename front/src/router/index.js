import { createRouter, createWebHistory } from 'vue-router'

import Home from '@/components/home/HomePage.vue'
import Editor from '@/components/editor/EditorPage.vue'
import New from '@/components/new/NewPage.vue'
import NewPrompt from '@/components/new/NewPromptPage.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { top: 0 }
  },
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/editor', name: 'editor', component: Editor },
    { path: '/new', name: 'new', component: New},
    { path: '/new-prompt', name: 'newPrompt', component: NewPrompt}
    // { path: '/:pathMatch(.*)*', name: '404', component: Page404  }
  ]
})

export default router
