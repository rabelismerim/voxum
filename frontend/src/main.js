import { createApp } from 'vue'
import { Quasar, Notify } from 'quasar'
import router from './router'
import App from './App.vue'

// Importe a fonte do Material Icons
import '@quasar/extras/material-icons/material-icons.css'

// Importe o CSS principal do Quasar
import 'quasar/src/css/index.sass'

// Importe o CSS da aplicação (Tailwind) por último
import './style.css'

const app = createApp(App)

app.use(Quasar, {
  plugins: { Notify }
})

app.use(router)
app.mount('#app')