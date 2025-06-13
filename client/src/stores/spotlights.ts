// Types & API
import type { Spotlight } from "@/types/spotlight"
import * as SpotlightAPI from "@/api/spotlight"
import { config } from "@/main"

/**
 * Only fetch spotlights once and store them.
 */
export const useSpotlightStore = defineStore("Spotlights", () => {
    // Fields
    const items = ref<Spotlight[]>()
    // Methods
    function fetchSpotlights() {
        // Dont keep refetching
        if (items.value) {
            return
        }

        SpotlightAPI.getSpotlights()
            .then((response) => {
                items.value = response.data
            })
            .catch(() => {
                if (location.hostname === "localhost") {
                    // fetch default spotlights from local config
                    import("@/assets/config/spotlights.json").then((module) => {
                        items.value = module.default as Spotlight[]
                    })
                } else {
                    // fetch default spotlights
                    fetch(config.spotlights.default).then((response) => response.json()).then((data) => {
                        items.value = data as Spotlight[]
                    })
                }
            })
    }
    // Export
    return {
        // Fields
        items,
        // Methods
        fetchSpotlights,
    }
})
