import { getNewYearsDay, getNewYearsEve, toFirstDayOfMonth, toLastDayOfMonth } from "@/ts/date"
import type { TrendSettings } from "@/types/trends"
import type { SelectLabel } from "@/types/ui"

export const useTrendSettings = defineStore("trendSettings", () => {
    // Fields
    const trendSettings = ref<TrendSettings>({
        year: { start: getNewYearsDay(), end: getNewYearsEve() }, // TODO if corpus.end
        month: { start: toFirstDayOfMonth(new Date()), end: toLastDayOfMonth(new Date()) },
        week: { start: new Date(), end: new Date() },
        other: { start: new Date(), end: new Date() },
        trendType: "keyness",
        modifier: 1,
        period: "month",
        ngram: 1,
    })
    const trendTypeOptions: SelectLabel[] = [
        { label: "keyness", value: "keyness" },
        { label: "absolute frequentie", value: "absolute" },
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
    // Lifecycle
    watch(
        () => ({ ...trendSettings.value }),
        (newValue, oldValue) => {
            const copy = { ...newValue }
            delete copy.language // language is allowed to be null
            const entries = Object.values(copy)
            if (entries.some((entry) => entry == null || entry == undefined)) {
                setTimeout(() => {
                    trendSettings.value = oldValue
                }, 0)
            }
        },
    )
    // Export
    return { trendSettings, trendTypeOptions, modifierOptions, periodOptions }
})
