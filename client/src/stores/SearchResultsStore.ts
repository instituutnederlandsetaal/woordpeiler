// Libraries & Stores
import { ref } from 'vue'
import { defineStore, storeToRefs } from 'pinia'
import { useSearchSettingsStore } from '@/stores/SearchSettingsStore'
import { useSearchItemsStore } from '@/stores/SearchItemsStore'
// Types & API
import type { SearchItem, GraphItem } from "@/types/Search"
import type { SearchResponse } from '@/api/search'
import * as SearchAPI from "@/api/search"
import { toTimestamp } from '@/ts/date'

export function displayName(str) {
    return Object.entries(str)
        .filter(([key, value]) => value && key !== "color")
        .map(([key, value]) => value)
        .join(" ")
}

export const useSearchResultsStore = defineStore('SearchResults', () => {
    // Fields
    const searchResults = ref<GraphItem[]>([])
    const { searchSettings } = storeToRefs(useSearchSettingsStore())
    const { searchItems } = storeToRefs(useSearchItemsStore())
    const isSearching = ref(false)
    // Methods
    function search() {
        isSearching.value = true
        // save cookies
        localStorage.setItem("dataSeries", JSON.stringify(searchItems.value))
        searchResults.value = []
        searchItems.value.forEach((ds) => getFrequency(ds))
    }

    function getFrequency(ds: SearchItem) {
        // param map
        const wordSearch = {
            wordform: ds.wordform?.trim()?.toLowerCase(),
            pos: ds.pos,
            lemma: ds.lemma,
            source: ds.newspaper,
            language: ds.language
        }

        // Remove falsy values, and blank strings (could be tabs and spaces)
        Object.keys(wordSearch).forEach(
            (key) => (wordSearch[key] == null || wordSearch[key].trim() === "") && delete wordSearch[key]
        )


        const searchRequest: SearchAPI.SearchRequest = {
            wordform: ds.wordform,
            lemma: ds.lemma,
            pos: ds.pos,
            source: ds.newspaper,
            language: ds.language,
            period_length: searchSettings.value.timeBucketSize,
            period_type: searchSettings.value.timeBucketType,
            start_date: toTimestamp(searchSettings.value.startDate),
            end_date: toTimestamp(searchSettings.value.endDate),
        }

        SearchAPI.getSearch(searchRequest)
            .then((response: SearchResponse) => {
                const dataset: GraphItem = {
                    datapoint: ds,
                    label: displayName(ds),
                    borderColor: `#${ds.color}`,
                    backgroundColor: `#${ds.color}`,
                    data: response.data.map((d) => {
                        return { x: d.time * 1000, y: parseFloat(d[searchSettings.value.frequencyType]) }
                    }),
                }
                searchResults.value.push(dataset)
            })
            .finally(() => {
                isSearching.value = false
            })
    }
    // Export
    return {
        // Fields
        searchResults, isSearching,
        // Methods
        search
    }
})