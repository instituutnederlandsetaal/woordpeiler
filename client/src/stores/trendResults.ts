// Stores
import { useTrendSettingsStore } from "@/stores/trendSettings"
// API
import * as TrendAPI from "@/api/trends"
import type { TrendRequest } from "@/api/trends"
// Types
import { type TrendSettings, type TrendResult, type DateRange } from "@/types/trends"

export const useTrendResultsStore = defineStore("TrendResults", () => {
    // Fields
    const { trendSettings } = storeToRefs(useTrendSettingsStore())
    const trendResults = ref<TrendResult[]>(null)
    const trendsLoading = ref(false)
    const lastTrendSettings = ref<TrendSettings>(null)
    // Methods
    function getTrends() {
        deepCopyLastUsedTrends()
        trendResults.value = []
        trendsLoading.value = true
        const selectedPeriod: DateRange = trendSettings.value[trendSettings.value.period]
        const trendRequest: TrendRequest = {
            trend_type: trendSettings.value.trendType,
            modifier: trendSettings.value.modifier,
            start: selectedPeriod.start,
            end: selectedPeriod.end,
            enriched: trendSettings.value.enriched,
            language: trendSettings.value.language,
            ascending: trendSettings.value.ascending,
            ngram: trendSettings.value.ngram,
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
    function deepCopyLastUsedTrends() {
        lastTrendSettings.value = JSON.parse(JSON.stringify(trendSettings.value))
        // reparse dates from string (JSON.stringify converts dates to strings)
        function parseDateRange(range: DateRange) {
            // technically it is a {start: string, end: string}
            range.start = new Date(range.start)
            range.end = new Date(range.end)
        }
        parseDateRange(lastTrendSettings.value.year)
        parseDateRange(lastTrendSettings.value.month)
        parseDateRange(lastTrendSettings.value.week)
        parseDateRange(lastTrendSettings.value.other)
    }
    // Export
    return {
        // Fields
        trendResults,
        trendsLoading,
        lastTrendSettings,
        // Methods
        getTrends,
    }
})
