import '@/assets/main.scss'
import '@/assets/primevue.scss'
import '@/assets/media.scss'
import 'primeicons/primeicons.css'
import { setAxiosBaseUrl } from './api/api';
setAxiosBaseUrl()

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config';
import Aura from '@primevue/themes/aura';

import App from './App.vue'
import router from './router'
import { isInternal } from '@/ts/internal';

// create app
const app = createApp(App)

// setup primevue
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.my-app-dark',
        }
    },
    locale: {
        monthNamesShort: ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'],
        monthNames: ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december'],
        dayNamesMin: ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'],
        firstDayOfWeek: 0,
        emptyFilterMessage: 'Geen resultaten',
        emptyMessage: 'Geen resultaten',
        emptySearchMessage: 'Geen resultaten',
    }
});
app.use(PrimeVue, { unstyled: true });

// setup pinia store
app.use(createPinia())

// setup router
app.use(router)

// global config
app.config.globalProperties.$internal = isInternal()

// launch app
app.mount('#app')
