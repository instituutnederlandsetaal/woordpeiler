// Libraries & Stores
import { getNewYearsDay, getNewYearsEve } from "@/ts/date"
import type { TrendSettings } from "@/types/trends"
import type { SelectLabel } from "@/types/UI"
import { defineStore } from "pinia"
import { ref } from "vue"

export const useTrendSettingsStore = defineStore('TrendSettings', () => {
    // Fields
    const trendSettings = ref<TrendSettings>({
        startDate: getNewYearsDay(),
        endDate: getNewYearsEve(),
        trendType: "absolute",
        modifier: 1,
    })
    const trendTypeOptions: SelectLabel[] = [
        { label: "keyness", value: "keyness" },
        { label: "absolute frequentie", value: "absolute" }
    ]
    const modifierOptions: Record<string, string> = {
        keyness: "Smoothingparameter",
        absolute: "Maximumfrequentie in referentiecorpus",
    }
    // Export
    return { trendSettings, trendTypeOptions, modifierOptions }
})