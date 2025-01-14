// Libraries & Stores
import { ref } from 'vue'
import { defineStore } from 'pinia'
// Types & API
import type { Spotlight } from '@/types/spotlight'
import * as DefaultSpotlights from "@/ts/defaultSpotlights"
import * as SpotlightAPI from "@/api/spotlight"

/**
 * Only fetch spotlights once and store them.
 */
export const useSpotlightStore = defineStore('Spotlights', () => {
    // Fields
    const items = ref<Spotlight[]>()
    // Methods
    function fetchSpotlights() {
        SpotlightAPI.getSpotlights().then((response) => {
            items.value = response.data
        }).catch(() => {
            items.value = DefaultSpotlights.items
        })
    }
    // Export
    return {
        // Fields
        items,
        // Methods
        fetchSpotlights
    }
})