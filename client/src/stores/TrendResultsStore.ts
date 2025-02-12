// Libraries
import { defineStore, storeToRefs } from "pinia"
import { ref } from "vue"
// Stores
import { useTrendSettingsStore } from "./TrendSettingsStore"
// API
import * as TrendAPI from "@/api/trends"
import type { TrendRequest } from "@/api/trends"
import { type TrendSettings, type TrendResult } from "@/types/trends"
// Utils
import { toTimestamp } from "@/ts/date"

export const useTrendResultsStore = defineStore('TrendResults', () => {
    // Fields
    const { trendSettings } = storeToRefs(useTrendSettingsStore())
    const trendResults = ref<TrendResult[]>(null)
    const trendsLoading = ref(false)
    const lastTrendSettings = ref<TrendSettings>(null)
    // Methods
    function getTrends() {
        lastTrendSettings.value = JSON.parse(JSON.stringify(trendSettings.value)) // deep copy
        trendResults.value = []
        trendsLoading.value = true
        const selectedPeriod: DateRange = trendSettings.value[trendSettings.value.period]
        const trendRequest: TrendRequest = {
            trend_type: trendSettings.value.trendType,
            modifier: trendSettings.value.modifier,
            start_date: toTimestamp(selectedPeriod.start),
            end_date: toTimestamp(selectedPeriod.end),
            enriched: trendSettings.value.enriched,
            language: trendSettings.value.language,
            ascending: trendSettings.value.ascending,
        }

        TrendAPI.getTrends(trendRequest)
            .then((response) => {
                trendResults.value = response.data
            })
            .finally(() => {
                trendsLoading.value = false
                // browser notification via document.title
                if (document.hidden) {
                    document.title = "(1) " + document.title
                    // reset on focus
                    document.addEventListener("visibilitychange", () => {
                        if (!document.hidden) {
                            document.title = document.title.replace("(1) ", "")
                        }
                    })
                }
            })
    }
    // Export
    return {
        // Fields
        trendResults, trendsLoading, lastTrendSettings,
        // Methods
        getTrends
    }
})