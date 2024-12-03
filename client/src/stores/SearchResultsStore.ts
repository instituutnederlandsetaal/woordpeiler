// Libraries & Stores
import { ref } from 'vue'
import { defineStore, storeToRefs } from 'pinia'
import { useSearchSettingsStore } from '@/stores/SearchSettingsStore'
import { useSearchItemsStore } from '@/stores/SearchItemsStore'
// Types & API
import { type SearchItem, type GraphItem, equalSearchItem } from "@/types/Search"
import type { SearchResponse } from '@/api/search'
import * as SearchAPI from "@/api/search"
import { toTimestamp } from '@/ts/date'

export function displayName(i: SearchItem): string {
    return `${i.wordform || ""} ${i.lemma || ""} ${i.pos || ""} ${i.newspaper || ""} ${i.language || ""}`
}

export const useSearchResultsStore = defineStore('SearchResults', () => {
    // Fields
    const searchResults = ref<GraphItem[]>([])
    const { searchSettings } = storeToRefs(useSearchSettingsStore())
    const { searchItems } = storeToRefs(useSearchItemsStore())
    const isSearching = ref(false)
    // Methods
    function search() {
        // save current search to local storage
        localStorage.setItem("searchItems", JSON.stringify(searchItems.value))

        // if search settings changed, all search results are invalidated
        const oldSearchSettings = JSON.parse(localStorage.getItem("searchSettings") || "{}")
        if (JSON.stringify(oldSearchSettings) !== JSON.stringify(searchSettings.value)) {
            searchResults.value = []
            localStorage.setItem("searchSettings", JSON.stringify(searchSettings.value))
        }

        // remove irrelevant search results
        searchResults.value = searchResults.value.filter((i) => searchItems.value.some((j) => equalSearchItem(i.datapoint, j)))
        // newly added search items
        const toBeSearched = searchItems.value.filter((i: SearchItem) => !searchResults.value.map((x) => x.datapoint).some((j) => equalSearchItem(i, j)))
        // search for each search item
        toBeSearched.forEach((ds) => getFrequency(ds))
        // only loading screen if we're searching
        if (toBeSearched.length > 0) {
            isSearching.value = true
        }
    }
    function getFrequency(item: SearchItem) {
        // construct search request, partly from unsanitized user input
        const searchRequest: SearchAPI.SearchRequest = {
            // unsanitized user input
            wordform: item.wordform?.trim()?.toLowerCase(),
            lemma: item.lemma?.trim()?.toLowerCase(),
            // fixed values
            pos: item.pos,
            source: item.newspaper,
            language: item.language,
            period_length: searchSettings.value.timeBucketSize,
            period_type: searchSettings.value.timeBucketType,
            start_date: toTimestamp(searchSettings.value.startDate),
            end_date: toTimestamp(searchSettings.value.endDate),
        }
        // loading icon per item
        item.loading = true

        SearchAPI.getSearch(searchRequest)
            .then((response: SearchResponse) => {
                const dataset: GraphItem = {
                    datapoint: item,
                    label: displayName(item),
                    data: response.data.map((d) => {
                        return { x: d.time * 1000, y: parseFloat(d[searchSettings.value.frequencyType]) }
                    }),
                }
                searchResults.value.push(dataset)
            })
            .finally(() => {
                isSearching.value = false
                item.loading = false
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