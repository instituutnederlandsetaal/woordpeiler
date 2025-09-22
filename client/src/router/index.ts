import { createRouter, createWebHistory, type Router } from "vue-router"
import { config } from "@/main"
import GraphView from "@/views/GraphView.vue"
import TrendsView from "@/views/TrendsView.vue"
import HelpView from "@/views/HelpView.vue"
import HomeView from "@/views/HomeView.vue"
import AboutView from "@/views/AboutView.vue"

const router = (): Router => {
    const r = createRouter({
        history: createWebHistory(config.basePath),
        routes: [
            { path: "/", component: HomeView, meta: { title: config.app.slogan } },
            { path: "/trends", name: "trends", component: TrendsView, meta: { title: "Trends" } },
            { path: "/help", component: HelpView, meta: { title: "Help" } },
            { path: "/grafiek", component: GraphView },
            { path: "/over", component: AboutView, meta: { title: "Over" } },
        ],
    })
    r.afterEach((to) => {
        if (to.meta.title) {
            document.title = `${config.app.name} - ${to.meta.title}`
        }
    })
    return r
}

export default router
