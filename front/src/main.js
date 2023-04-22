import { createApp } from 'vue'
import { Quasar, Dialog, Notify } from 'quasar'

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
app.use(router)

app.mount('#app')
