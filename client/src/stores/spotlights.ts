import type { SpotlightSection } from "@/types/spotlight"
import * as SpotlightAPI from "@/api/spotlight"
import { config } from "@/main"

/** Only fetch spotlights once and store them. */
export const useSpotlightStore = defineStore("spotlights", () => {
    const items = ref<SpotlightSection[]>()
    function fetch() {
        SpotlightAPI.getSpotlights()
            .then((response) => {
                items.value = response.data
            })
            .catch(() => {
                // Could not connect to ivdnt
                if (location.hostname === "localhost") {
                    // fetch default spotlights from local config
                    import("@/assets/config/spotlights.json").then((module) => {
                        items.value = module.default as SpotlightSection[]
                    })
                } else {
                    // fetch default spotlights as backup
                    window.fetch(config.spotlights.default)
                        .then((response) => response.json())
                        .then((data) => (items.value = data))
                }
            })
    }
    fetch()
    return { items, fetch }
})
