import { defineStore, storeToRefs } from "pinia"
import { useTrendSettingsStore } from "./TrendSettingsStore"
import { ref } from "vue"
import type { TrendResult } from "@/types/trends"
import * as TrendAPI from "@/api/trends"
import { tr } from "date-fns/locale"

export const useTrendResultsStore = defineStore('TrendResults', () => {
    // Fields
    const { trendSettings } = storeToRefs(useTrendSettingsStore())
    const trendResults = ref<TrendResult[]>([])
    const trendsLoading = ref(false)
    // Methods
    function getTrends() {
        trendResults.value = []
        trendsLoading.value = true
        TrendAPI.getTrends(trendSettings.value)
            .then((response) => {
                trendResults.value = response.data
            })
            .finally(() => {
                trendsLoading.value = false
            })
    }
    // Export
    return {
        // Fields
        trendResults, trendsLoading,
        // Methods
        getTrends
    }
})