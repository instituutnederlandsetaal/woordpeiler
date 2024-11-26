// Libraries & Stores
import { ref } from 'vue'
import { defineStore } from 'pinia'
// Types & API
import type { SearchSettings } from "@/types/Search"
import type { SelectLabel } from '@/types/UI'

export const useSearchSettingsStore = defineStore('SearchSettings', () => {
    // Fields
    const searchSettings = ref<SearchSettings>({
        timeBucketType: "year",
        timeBucketSize: 1,
        startDate: new Date('2000-01-01'),
        endDate: new Date(), // now
        frequencyType: "rel_freq",
    })
    const frequencyTypeOptions: SelectLabel[] = [
        { label: "relatief", value: "rel_freq" },
        { label: "absoluut", value: "abs_freq" },
    ]
    const timeBucketOptions: SelectLabel[] = [
        { label: "dag", value: "day" },
        { label: "week", value: "week" },
        { label: "maand", value: "month" },
        { label: "jaar", value: "year" },
    ]
    // Export
    return { searchSettings, frequencyTypeOptions, timeBucketOptions }
})
