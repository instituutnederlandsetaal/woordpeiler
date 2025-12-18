import type { Woordpeiling } from "@/types/spotlight"
import * as API from "@/api/woordpeiling"
import { config } from "@/main"

export const useWoordpeiling = defineStore("woordpeiling", () => {
    const woordpeiling = ref<Woordpeiling>()

    function fetch() {
        API.getWoordpeiling()
            .then((res) => {
                // Could be old version
                if (res.version !== config.version) {
                    return Promise.reject("Wrong version")
                }
                woordpeiling.value = res
            })
            .catch(() => {
                // Could not connect to ivdnt or wrong version
                if (location.hostname === "localhost") {
                    // fetch default spotlights from local config
                    import("@/assets/config/woordpeiling.json").then((module) => {
                        woordpeiling.value = module.default as Woordpeiling
                    })
                }
            })
    }

    fetch()

    return { woordpeiling }
})
