// Libraries
import { createRouter, createWebHistory } from "vue-router"
import { config } from "@/main"
// Views
import SearchView from "@/views/SearchView.vue"
import TrendsView from "@/views/TrendsView.vue"
import HelpView from "@/views/HelpView.vue"
import HomeView from "@/views/HomeView.vue"
import AboutView from "@/views/AboutView.vue"

const router = () =>
    createRouter({
        history: createWebHistory(config.basePath),
        routes: [
            { path: "/", component: HomeView },
            { path: "/trends", name: "trends", component: TrendsView },
            { path: "/help", component: HelpView },
            { path: "/grafiek", component: SearchView },
            { path: "/over", component: AboutView },
        ],
    })

export default router
