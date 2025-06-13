import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import vueDevTools from "vite-plugin-vue-devtools"
import AutoImport from "unplugin-auto-import/vite"
import Components from "unplugin-vue-components/vite"
import { PrimeVueResolver } from "@primevue/auto-import-resolver"

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        vueDevTools(),
        AutoImport({ imports: ["vue", "pinia", "vue-router"], dts: true }),
        Components({ dts: true, resolvers: [PrimeVueResolver()] }),
    ],
    server: { watch: { usePolling: true } },
    resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
    // remove initial slash
    experimental: { renderBuiltUrl: (fileName: string, _) => fileName.slice(1) },
})
