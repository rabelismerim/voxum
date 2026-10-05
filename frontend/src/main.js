import { createApp } from 'vue'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'
import { Dialog, Quasar, Ripple } from 'quasar'
import quasarLang from 'quasar/lang/pt-BR'
import quasarIconSet from 'quasar/icon-set/material-icons-outlined'

import router from '@/router'
import App from '@/App.vue'

// Diretivas personalizadas
import vResize from '@/directives/vResize'

// Estilos
import '@quasar/extras/material-icons-outlined/material-icons-outlined.css'
import 'quasar/src/css/index.sass'
import '@/assets/style.css'
import '@unocss/reset/tailwind.css'
import 'uno.css'

const app = createApp(App)

app.use(Quasar, {
  plugins: {
    Dialog,
  },
  lang: quasarLang,
  iconSet: quasarIconSet,
  config: {
    brand: {
      primary: '#007db3',
      secondary: '#111111',
      accent: '#111111',
      dark: '#111111',
      positive: '#007db3',
      negative: '#d9291c',
      info: '#31CCEC',
      warning: '#F2C037',
    },
  },
})

app.use(router)
app.use(autoAnimatePlugin)

// Registo de diretivas
app.directive('ripple', Ripple)
app.directive('resize', vResize)

app.mount('#app')