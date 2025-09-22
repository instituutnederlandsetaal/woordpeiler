// Libraries & Stores
import { v4 as uuidv4 } from "uuid"
import { useSearchSettingsStore } from "@/stores/searchSettings"
import { useSearchItemsStore } from "@/stores/searchItems"
// Types & API
import {
    type SearchItem,
    type GraphItem,
    equalSearchItem,
    type SearchSettings,
    equalSearchSettings,
    displayName,
    toIntervalStr,
} from "@/types/search"
import * as SearchAPI from "@/api/search"
// Utils
import { toTimestamp } from "@/ts/date"
import { plausibleWordsEvent } from "@/ts/plausible"
import { config } from "@/main"

export const useSearchResultsStore = defineStore("SearchResults", () => {
    // Fields
    const router = useRouter()
    const searchResults = ref<GraphItem[]>([])
    const { searchSettings } = storeToRefs(useSearchSettingsStore())
    const { validSearchItems, languageOptions } = storeToRefs(useSearchItemsStore())
    const isSearching = ref(false)
    const lastSearchSettings = ref<SearchSettings>()
    function search() {
        // Methods
        // Scroll to top of page
        window.scrollTo({ top: 0 }) // behavior: "smooth" not supported in firefox under certain conditions, like when switching views

        // save current search to local storage
        localStorage.setItem("searchItems", JSON.stringify(validSearchItems.value))
        lastSearchSettings.value = JSON.parse(JSON.stringify(searchSettings.value))

        // set them as url params
        setSearchParamsInUrl()
        // set window title, but only if we are not on the trends page
        if (router.currentRoute.value.name != "trends")
            document.title = `${config.app.name} - ` + validSearchItems.value.map((i) => displayName(i)).join(", ")

        // if search settings changed, all search results are invalidated
        const oldSearchSettings = JSON.parse(localStorage.getItem("searchSettings") || "{}")
        // reparse dates
        oldSearchSettings.startDate = new Date(oldSearchSettings.startDate)
        oldSearchSettings.endDate = new Date(oldSearchSettings.endDate)

        if (!equalSearchSettings(oldSearchSettings, searchSettings.value)) {
            searchResults.value = []
            localStorage.setItem("searchSettings", JSON.stringify(searchSettings.value))
        }

        // remove irrelevant search results
        searchResults.value = searchResults.value.filter((i) =>
            validSearchItems.value.some((j) => equalSearchItem(i.searchItem, j)),
        )
        // newly added search items
        const toBeSearched = validSearchItems.value.filter(
            (i: SearchItem) => !searchResults.value.map((x) => x.searchItem).some((j) => equalSearchItem(i, j)),
        )
        // search for each search item
        toBeSearched.forEach((ds) => {
            if (searchSettings.value.languageSplit && !(ds.language || ds.source)) {
                // split by language, but only if language or source is not set
                const colors = config.search.autosplit.colors
                languageOptions.value.forEach((lang) => {
                    getFrequency({ ...ds, language: lang, color: colors[lang] })
                })
                // also add the original search item
                // time out to add it last
                // setTimeout(() => {
                //     getFrequency(ds)
                // }, 100)
            } else {
                // only one search
                getFrequency(ds)
            }
        })
        // only show loading screen and send to plausible if we're searching
        if (toBeSearched.length > 0) {
            isSearching.value = true
            plausibleWordsEvent("grafiek", searchSettings.value, validSearchItems.value)
        }
    }
    function getFrequency(item: SearchItem) {
        // construct search request, partly from unsanitized user input
        const searchRequest: SearchAPI.SearchRequest = {
            // unsanitized user input
            w: item.wordform?.trim()?.toLowerCase(),
            l: item.lemma?.trim()?.toLowerCase(),
            // fixed values
            p: item.pos,
            s: item.source,
            v: item.language,
            i: toIntervalStr(searchSettings.value.intervalType, searchSettings.value.intervalLength),
            start: toTimestamp(searchSettings.value.startDate),
            end: toTimestamp(searchSettings.value.endDate),
        }
        // loading icon per item
        item.loading = true

        SearchAPI.getSearch(searchRequest)
            .then((res) => {
                const dataset: GraphItem = {
                    searchItem: JSON.parse(JSON.stringify(item)),
                    uuid: uuidv4(),
                    data: {
                        abs_freq: res.data.map((i) => ({ x: i[0] * 1000, y: i[1] })),
                        rel_freq: res.data.map((i) => ({ x: i[0] * 1000, y: i[2] })),
                    },
                }
                searchResults.value.push(dataset)
            })
            .finally(() => {
                isSearching.value = false
                item.loading = false
            })
    }
    function searchItemPropToUrlStr(items: SearchItem[], prop: string): string | undefined {
        const split = ","
        const itemStrs: string[] | undefined = items.map((i) => i[prop] || "")
        return itemStrs.every((i) => i == "") ? undefined : itemStrs.join(split)
    }

    function setSearchParamsInUrl() {
        const paramsObj = {
            w: searchItemPropToUrlStr(validSearchItems.value, "wordform"),
            l: searchItemPropToUrlStr(validSearchItems.value, "lemma"),
            p: searchItemPropToUrlStr(validSearchItems.value, "pos"),
            s: searchItemPropToUrlStr(validSearchItems.value, "source"),
            v: searchItemPropToUrlStr(validSearchItems.value, "language"),
            c: searchItemPropToUrlStr(validSearchItems.value, "color"),
            i: toIntervalStr(searchSettings.value.intervalType, searchSettings.value.intervalLength),
            il: undefined, // remove legacy interval length
            f: searchSettings.value.frequencyType.split("_")[0], // f for frequency
            start: toTimestamp(searchSettings.value.startDate),
            end: toTimestamp(searchSettings.value.endDate),
        }
        // router without history (needs timeout to avoid too many history calls error)
        setTimeout(() => {
            router.replace({ query: { ...router.currentRoute.value.query, ...paramsObj } })
        }, 300)
    }
    // Lifecycle
    /** ensure that color and visibility updates to search items also update the result items */
    watch(
        () => validSearchItems.value,
        () => {
            // for each search item, try to find the corresponding search result (using equalSearchItem())
            searchResults.value.forEach((result) => {
                // find the corresponding search item
                const searchItem = validSearchItems.value.find((item) => equalSearchItem(item, result.searchItem))
                // if found, update the color and visibility
                if (searchItem) {
                    result.searchItem.color = searchItem.color
                    result.searchItem.visible = searchItem.visible
                }
            })
        },
        { deep: true },
    )
    // Export
    return {
        // Fields
        searchResults,
        isSearching,
        lastSearchSettings,
        // Methods
        search,
    }
})
