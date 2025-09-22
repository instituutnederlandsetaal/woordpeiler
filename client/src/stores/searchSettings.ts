// Types & API
import type { SearchSettings } from "@/types/search"
import type { SelectLabel } from "@/types/ui"
import { config } from "@/main"
import { toUTCDate } from "@/ts/date"

export const useSearchSettingsStore = defineStore("SearchSettings", () => {
    // Fields
    const searchSettings = ref<SearchSettings>({
        intervalType: initTimeBucket().type,
        intervalLength: initTimeBucket().size,
        startDate: new Date(config.period.start),
        endDate: config.period.end ? new Date(config.period.end) : toUTCDate(new Date()),
        frequencyType: "rel_freq",
        languageSplit: false,
    })
    const frequencyTypeOptions: SelectLabel[] = [
        { label: "relatief", value: "rel_freq" },
        { label: "absoluut", value: "abs_freq" },
    ]
    const timeBucketOptions: SelectLabel[] = [
        { label: "week", value: "w" },
        { label: "maand", value: "m" },
        { label: "jaar", value: "y" },
        { label: "dag", value: "d" },
    ]
    function loadSearchSettings() {
        if (localStorage.getItem("searchSettings")) {
            searchSettings.value = JSON.parse(localStorage.getItem("searchSettings"))
            // convert to Date
            searchSettings.value.startDate = new Date(searchSettings.value.startDate)
            searchSettings.value.endDate = new Date(searchSettings.value.endDate)
        }
    }
    function resetDates() {
        searchSettings.value.startDate = new Date(config.period.start)
        searchSettings.value.endDate = config.period.end ? new Date(config.period.end) : toUTCDate(new Date())
    }
    function readUrlParams() {
        const params = new URLSearchParams(window.location.search)
        const interval = params.get("i")
        const legacyIntervalLength = params.get("il")
        const startDate = params.get("start")
        const endDate = params.get("end")
        const frequencyType = params.get("f")

        if (interval) {
            if (interval.match(/\d/)) {
                // new format
                searchSettings.value.intervalType = interval.slice(-1)
                searchSettings.value.intervalLength = parseInt(interval.slice(0, -1))
            } else {
                // legacy format
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

        const freqMap = { rel: "rel_freq", abs: "abs_freq" }
        if (frequencyType) searchSettings.value.frequencyType = freqMap[frequencyType]
    }
    function initTimeBucket(): { type: string; size: number } {
        return window.innerWidth < 768 ? config.search.interval.mobile : config.search.interval.desktop
    }
    // Lifecycle
    watch(
        () => ({ ...searchSettings.value }),
        (newValue, oldValue) => {
            const entries = Object.values(newValue)
            if (entries.some((entry) => entry == null || entry == undefined)) {
                setTimeout(() => {
                    searchSettings.value = oldValue
                }, 0)
            }
        },
    )
    // Export
    return {
        // Fields
        searchSettings,
        frequencyTypeOptions,
        timeBucketOptions,
        // Methods
        loadSearchSettings,
        resetDates,
        readUrlParams,
    }
})
