// Libraries & Stores
import { ref, watch } from 'vue'
import { defineStore } from 'pinia'
// Types & API
import type { SearchSettings } from "@/types/Search"
import type { SelectLabel } from '@/types/UI'
import { isInternal } from '@/ts/internal'
import { toMidnightUTC, toUTCDate } from '@/ts/date'

export const useSearchSettingsStore = defineStore('SearchSettings', () => {
    // Fields
    const searchSettings = ref<SearchSettings>({
        intervalType: initTimeBucket().type,
        intervalLength: initTimeBucket().size,
        startDate: new Date('1600-01-01'),
        endDate: new Date('1700-01-01'),
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
            { label: "week", value: "w" },
            { label: "maand", value: "m" },
            { label: "jaar", value: "y" },
        ]
        // For now always true, could be set back to internal
        const showDaySetting = true // isInternal()
        if (showDaySetting) {
            opts.unshift({ label: "dag", value: "d" })
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
        searchSettings.value.startDate = new Date('1600-01-01')
        searchSettings.value.endDate = new Date('1701-01-01')
    }
    function readUrlParams() {
        const params = new URLSearchParams(window.location.search)
        const interval = params.get('i')
        const legacyIntervalLength = params.get('il')
        const startDate = params.get('start')
        const endDate = params.get('end')
        const frequencyType = params.get('f')

        if (interval) {
            if (interval.match(/\d/)) { // new format
                searchSettings.value.intervalType = interval.slice(-1)
                searchSettings.value.intervalLength = parseInt(interval.slice(0, -1))
            } else { // legacy format
                searchSettings.value.intervalType = interval[0]
                if (legacyIntervalLength) searchSettings.value.intervalLength = parseInt(legacyIntervalLength)
            }
        }
        /** dateStr is either a unix time stamp or a date string like YYYY-MM-DD */
        function toDate(dateStr: string): Date {
            if (dateStr.includes("-")) return new Date(dateStr)
            return new Date(parseInt(dateStr) * 1000)
        }

        if (startDate) searchSettings.value.startDate = toDate(startDate)
        if (endDate) searchSettings.value.endDate = toDate(endDate)

        const freqMap = {
            "rel": "rel_freq",
            "abs": "abs_freq"
        }
        if (frequencyType) searchSettings.value.frequencyType = freqMap[frequencyType]
    }
    function initTimeBucket(): { type: string, size: number } {
        const desktop = { type: "m", size: 3 }
        const mobile = { type: "y", size: 1 }
        const isMobile = window.innerWidth < 768
        return isMobile ? mobile : desktop
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
