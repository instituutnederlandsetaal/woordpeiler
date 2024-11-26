// Libraries & Stores
import type { TrendSettings } from "@/types/trends"
import type { SelectLabel } from "@/types/UI"
import { defineStore } from "pinia"
import { ref } from "vue"

export const useTrendSettingsStore = defineStore('TrendSettings', () => {
    // Fields
    const trendSettings = ref<TrendSettings>({
        periodType: "year",
        periodLength: 1,
        trendType: "absolute",
        modifier: 1,
    })
    const timeBucketOptions: SelectLabel[] = [
        { label: "week", value: "week" },
        { label: "maand", value: "month" },
        { label: "jaar", value: "year" },
    ]
    const trendTypeOptions: SelectLabel[] = [
        { label: "keyness", value: "keyness" },
        { label: "absolute frequentie", value: "absolute" }
    ]
    const modifierOptions: Record<string, string> = {
        keyness: "Smoothingparameter",
        absolute: "Maximumfrequentie in referentiecorpus",
    }
    // Export
    return { trendSettings, timeBucketOptions, trendTypeOptions, modifierOptions }
})