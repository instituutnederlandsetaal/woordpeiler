import "@/assets/main.scss"
import "@/assets/primevue.scss"
import "@/assets/media.scss"
import "primeicons/primeicons.css"
import { setAxiosBaseUrl } from "@/api/api"

import PrimeVue from "primevue/config"
import Aura from "@primeuix/themes/aura"

import App from "@/App.vue"
import router from "@/router"
import { isInternal } from "@/ts/internal"

// create app
const app = createApp(App)

// setup primevue
app.use(PrimeVue, {
    theme: { preset: Aura, options: { darkModeSelector: ".my-app-dark" } },
    locale: {
        monthNamesShort: ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"],
        monthNames: [
            "januari",
            "februari",
            "maart",
            "april",
            "mei",
            "juni",
            "juli",
            "augustus",
            "september",
            "oktober",
            "november",
            "december",
        ],
        dayNamesMin: ["ma", "di", "wo", "do", "vr", "za", "zo"],
        firstDayOfWeek: 0,
        emptyFilterMessage: "Geen resultaten",
        emptyMessage: "Geen resultaten",
        emptySearchMessage: "Geen resultaten",
    },
})
app.use(PrimeVue, { unstyled: true })

// setup pinia store
app.use(createPinia())

// setup router
app.use(router)

// global config
app.config.globalProperties.$internal = isInternal()
await fetch("/config.json")
    .then((response) => response.json())
    .then((config) => {
        app.config.globalProperties.$config = config
    })
export const config = app.config.globalProperties.$config

document.documentElement.style.setProperty("--theme", app.config.globalProperties.$config.theme.color)
document.title = app.config.globalProperties.$config.appName
// set description
document
    .querySelector("meta[name='description']")
    ?.setAttribute("content", app.config.globalProperties.$config.app.description)
// set favicon
const favicon = document.querySelector("link[rel='icon']")
favicon?.setAttribute("href", app.config.globalProperties.$config.theme.favicon)

setAxiosBaseUrl()
// launch app
app.mount("#app")
