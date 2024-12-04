// Libraries
import { defineStore, storeToRefs } from "pinia"
import { ref } from "vue"
// Stores
import { useTrendSettingsStore } from "./TrendSettingsStore"
// API
import * as TrendAPI from "@/api/trends"
import type { TrendRequest } from "@/api/trends"
import type { TrendResult } from "@/types/trends"
// Utils
import { toTimestamp } from "@/ts/date"

export const useTrendResultsStore = defineStore('TrendResults', () => {
    // Fields
    const { trendSettings } = storeToRefs(useTrendSettingsStore())
    const trendResults = ref<TrendResult[]>([])
    const trendsLoading = ref(false)
    // Methods
    function getTrends() {
        trendResults.value = []
        trendsLoading.value = true
        const selectedPeriod: DateRange = trendSettings.value[trendSettings.value.period]
        const trendRequest: TrendRequest = {
            trend_type: trendSettings.value.trendType,
            modifier: trendSettings.value.modifier,
            start_date: toTimestamp(selectedPeriod.start),
            end_date: toTimestamp(selectedPeriod.end),
        }

        TrendAPI.getTrends(trendRequest)
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