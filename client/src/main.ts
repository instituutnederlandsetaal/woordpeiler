import "@/assets/main.scss"
import "@/assets/primevue.scss"
import "@/assets/media.scss"
import "primeicons/primeicons.css"
import { setAxiosBaseUrl } from "@/api"
import router from "@/router"

import PrimeVue from "primevue/config"
import Aura from "@primeuix/themes/aura"

import App from "@/App.vue"
import type { Config } from "@/ts/config"

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

// global config
export let config: Config = {}

if (location.hostname === "localhost") {
    import("@/assets/config/config.json").then((module) => {
        setConfigAndMount(module.default)
    })
} else {
    fetch("assets/config/config.json")
        .then((response) => response.json())
        .then(setConfigAndMount)
}

function setConfigAndMount(conf: Record<string, any>) {
    app.config.globalProperties.$config = conf
    config = conf
    app.config.globalProperties.$internal = config.internal
    // set theme
    document.documentElement.style.setProperty("--theme", config.theme.color)
    // set description
    const desc = document.createElement("meta")
    desc.name = "description"
    desc.content = config.app.description
    document.head.appendChild(desc)
    // set favicon
    const favicon = document.createElement("link")
    favicon.rel = "icon"
    favicon.href = config.theme.favicon
    document.head.appendChild(favicon)
    // set api
    setAxiosBaseUrl()
    // setup router
    app.use(router())
    // launch app
    app.mount("#app")
}
