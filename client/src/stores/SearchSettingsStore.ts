// Libraries & Stores
import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
// Types & API
import type { SearchSettings } from "@/types/Search"
import type { SelectLabel } from '@/types/UI'
import { isInternal } from '@/ts/internal'

export const useSearchSettingsStore = defineStore('SearchSettings', () => {
    // Fields
    const searchSettings = ref<SearchSettings>({
        timeBucketType: "month",
        timeBucketSize: 3,
        startDate: new Date('2000-01-01'),
        endDate: new Date(), // now
        frequencyType: "rel_freq",
        languageSplit: false,
    })
    const frequencyTypeOptions: SelectLabel[] = [
        { label: "relatief", value: "rel_freq" },
        { label: "absoluut", value: "abs_freq" },
    ]
    const timeBucketOptions: SelectLabel[] = initTimeBucketOpts()
    // Methods
    function initTimeBucketOpts(): SelectLabel[] {
        const opts = [
            { label: "week", value: "week" },
            { label: "maand", value: "month" },
            { label: "jaar", value: "year" },
        ]
        if (isInternal()) {
            opts.unshift({ label: "dag", value: "day" })
        }
        return opts
    }
    function loadSearchSettings() {
        if (localStorage.getItem("searchSettings")) {
            searchSettings.value = JSON.parse(localStorage.getItem("searchSettings"))
            // convert to Date
            searchSettings.value.startDate = new Date(searchSettings.value.startDate)
            searchSettings.value.endDate = new Date(searchSettings.value.endDate)
        }
    }
    function resetDates() {
        searchSettings.value.startDate = new Date('2000-01-01')
        searchSettings.value.endDate = new Date()
    }
    function readUrlParams() {
        const params = new URLSearchParams(window.location.search)
        const timeBucketType = params.get('pt')
        const timeBucketSize = params.get('ps')
        const startDate = params.get('start')
        const endDate = params.get('end')
        if (timeBucketType) searchSettings.value.timeBucketType = timeBucketType
        if (timeBucketSize) searchSettings.value.timeBucketSize = parseInt(timeBucketSize)
        if (startDate) searchSettings.value.startDate = new Date(parseInt(startDate) * 1000)
        if (endDate) searchSettings.value.endDate = new Date(parseInt(endDate) * 1000)
    }
    // Lifecycle
    watch(() => ({ ...searchSettings.value }), (newValue, oldValue) => {
        const entries = Object.values(newValue)
        if (entries.some(entry => entry == null || entry == undefined)) {
            setTimeout(() => {
                searchSettings.value = oldValue
            }, 0)
        }
    })
    // Export
    return {
        // Fields
        searchSettings, frequencyTypeOptions, timeBucketOptions,
        // Methods
        loadSearchSettings, resetDates, readUrlParams
    }
})
