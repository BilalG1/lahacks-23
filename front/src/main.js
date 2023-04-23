import { createApp } from 'vue'
import { Quasar, Dialog, Notify } from 'quasar'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import '@quasar/extras/material-icons/material-icons.css'
import '@/assets/main.css'
import 'quasar/src/css/index.sass'

import router from './router'
import App from './App.vue'

const app = createApp(App)
app.use(Quasar, {
  plugins: { Dialog, Notify },
  // config: { notify: { position: 'top' } }
})
app.use(ElementPlus)
app.use(router)

app.mount('#app')
