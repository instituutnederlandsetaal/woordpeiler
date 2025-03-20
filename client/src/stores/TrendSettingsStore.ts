// Libraries & Stores
import { getNewYearsDay, getNewYearsEve, toFirstDayOfMonth, toLastDayOfMonth } from "@/ts/date"
import type { TrendSettings } from "@/types/trends"
import type { SelectLabel } from "@/types/UI"
import { defineStore } from "pinia"
import { ref, watch } from "vue"

export const useTrendSettingsStore = defineStore('TrendSettings', () => {
    // Fields
    const trendSettings = ref<TrendSettings>({
        year: { start: new Date("1618-01-01"), end: new Date("1618-12-31") },
        month: { start: toFirstDayOfMonth(new Date("1618-01-01")), end: toLastDayOfMonth(new Date("1618-01-01")) },
        week: { start: new Date("1618-01-01"), end: new Date("1618-01-01") },
        other: { start: new Date("1690-01-01"), end: new Date("1701-01-01") },
        trendType: "absolute",
        modifier: 1,
        period: "year",
        enriched: true,
        ascending: false,
        ngram: 1,
    })
    const trendTypeOptions: SelectLabel[] = [
        { label: "keyness", value: "keyness" },
        { label: "absolute frequentie", value: "absolute" }
    ]
    const modifierOptions: Record<string, string> = {
        keyness: "Smoothingparameter",
        absolute: "Maximumfrequentie in referentiecorpus",
    }
    const periodOptions: SelectLabel[] = [
        { label: "week", value: "week" },
        { label: "maand", value: "month" },
        { label: "jaar", value: "year" },
        { label: "anders", value: "other" },
    ]
    const ngramOptions: SelectLabel[] = [
        { label: "1-gram", value: 1 },
        { label: "2-gram", value: 2 },
        { label: "3-gram", value: 3 },
        { label: "4-gram", value: 4 }
    ]
    // Lifecycle
    watch(() => ({ ...trendSettings.value }), (newValue, oldValue) => {
        const copy = { ...newValue }
        delete copy.language // langauge is allowed to be null
        const entries = Object.values(copy)
        if (entries.some(entry => entry == null || entry == undefined)) {
            setTimeout(() => {
                trendSettings.value = oldValue
            }, 0)
        }
    })
    // Export
    return { trendSettings, trendTypeOptions, modifierOptions, periodOptions, ngramOptions }
})