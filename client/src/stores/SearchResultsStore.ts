// Libraries & Stores
import { ref, watch } from 'vue'
import { defineStore, storeToRefs } from 'pinia'
import { useSearchSettingsStore } from '@/stores/SearchSettingsStore'
import { useSearchItemsStore } from '@/stores/SearchItemsStore'
// Types & API
import { type SearchItem, type GraphItem, equalSearchItem, type SearchSettings } from "@/types/Search"
import type { SearchResponse } from '@/api/search'
import * as SearchAPI from "@/api/search"
import { toTimestamp } from '@/ts/date'
import { v4 as uuidv4 } from 'uuid';

export const useSearchResultsStore = defineStore('SearchResults', () => {
    // Fields
    const searchResults = ref<GraphItem[]>([])
    const { searchSettings } = storeToRefs(useSearchSettingsStore())
    const { searchItems } = storeToRefs(useSearchItemsStore())
    const isSearching = ref(false)
    const lastSearchSettings = ref<SearchSettings>(null)
    // Methods
    function search() {
        // save current search to local storage
        localStorage.setItem("searchItems", JSON.stringify(searchItems.value))
        lastSearchSettings.value = JSON.parse(JSON.stringify(searchSettings.value))

        // if search settings changed, all search results are invalidated
        const oldSearchSettings = JSON.parse(localStorage.getItem("searchSettings") || "{}")
        if (JSON.stringify(oldSearchSettings) !== JSON.stringify(searchSettings.value)) {
            searchResults.value = []
            localStorage.setItem("searchSettings", JSON.stringify(searchSettings.value))
        }

        // remove irrelevant search results
        searchResults.value = searchResults.value.filter((i) => searchItems.value.some((j) => equalSearchItem(i.searchItem, j)))
        // newly added search items
        const toBeSearched = searchItems.value.filter((i: SearchItem) => !searchResults.value.map((x) => x.searchItem).some((j) => equalSearchItem(i, j)))
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
                    searchItem: JSON.parse(JSON.stringify(item)),
                    uuid: uuidv4(),
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
    // Lifecycle
    /** ensure that color and visibility updates to search items also update the result items */
    watch(() => searchItems.value, () => {
        // for each search item, try to find the corresponding search result (using equalSearchItem())
        searchResults.value.forEach((result) => {
            // find the corresponding search item
            const searchItem = searchItems.value.find((item) => equalSearchItem(item, result.searchItem))
            // if found, update the color and visibility
            if (searchItem) {
                result.searchItem.color = searchItem.color
                result.searchItem.visible = searchItem.visible
            }
        })
    }, { deep: true })
    // Export
    return {
        // Fields
        searchResults, isSearching, lastSearchSettings,
        // Methods
        search
    }
})