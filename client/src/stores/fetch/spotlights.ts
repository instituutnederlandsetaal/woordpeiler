import type { SpotlightConfig } from "@/types/spotlight"
import * as API from "@/api/spotlight"
import { config } from "@/main"

export const useSpotlights = defineStore("spotlights", () => {
    const spotlight = ref<SpotlightConfig>()

    function fetch() {
        API.getSpotlights()
            .then((res) => {
                // Could be old version
                if (res.data.version !== "2.0.0") {
                    return Promise.reject("Wrong version")
                }
                spotlight.value = res.data
            })
            .catch(() => {
                // Could not connect to ivdnt
                if (location.hostname === "localhost") {
                    // fetch default spotlights from local config
                    import("@/assets/config/spotlights.json").then((module) => {
                        spotlight.value = module.default as SpotlightConfig
                    })
                } else {
                    // Try via proxy
                    API.getProxiedSpotlights()
                        .then((res) => {
                            // Could be old version
                            if (res.data.version !== "2.0.0") {
                                return Promise.reject("Wrong version")
                            }
                            spotlight.value = res.data
                        })
                        .catch(() => {
                            // fetch default spotlights as backup
                            window
                                .fetch(config.spotlights.default)
                                .then((response) => response.json())
                                .then((data) => (spotlight.value = data))
                        })
                }
            })
    }

    fetch()

    return { spotlight }
})
