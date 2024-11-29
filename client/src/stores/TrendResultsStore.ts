import { defineStore, storeToRefs } from "pinia"
import { useTrendSettingsStore } from "./TrendSettingsStore"
import { ref } from "vue"
import type { TrendResult } from "@/types/trends"
import * as TrendAPI from "@/api/trends"
import type { TrendRequest } from "@/api/trends"
import { tr } from "date-fns/locale"
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
        const trendRequest: TrendRequest = {
            trend_type: trendSettings.value.trendType,
            modifier: trendSettings.value.modifier,
            start_date: toTimestamp(trendSettings.value.startDate),
            end_date: toTimestamp(trendSettings.value.endDate),
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