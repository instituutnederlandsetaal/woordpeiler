// Libraries & Stores
import { useSearchSettings } from "@/stores/search/searchSettings"
import { useSearchItems } from "@/stores/search/searchItems"
// Types & API
import { type SearchItem, equalSearchItem, searchToString, termPropToString } from "@/types/search"
import { type GraphItem } from "@/types/graph"
import { type SearchSettings, equalSearchSettings, toIntervalStr } from "@/types/searchSettings"
import * as SearchAPI from "@/api/search"
// Utils
import { toTimestamp } from "@/ts/date"
import { plausibleWordsEvent } from "@/ts/plausible"
import { config } from "@/main"
import { useLanguages } from "@/stores/fetch/languages"
import { v4 as uuidv4 } from "uuid"

export const useSearchResults = defineStore("searchResults", () => {
    // Fields
    const router = useRouter()
    const searchResults = ref<GraphItem[]>([])
    const { searchSettings } = storeToRefs(useSearchSettings())
    const { validSearchItems } = storeToRefs(useSearchItems())
    const { rawOptions: languageOptions } = storeToRefs(useLanguages())
    const isSearching = ref(false)
    const lastSearchSettings = ref<SearchSettings>()
    function search() {
        // Methods
        // Scroll to top of page
        window.scrollTo({ top: 0 }) // behavior: "smooth" not supported in firefox under certain conditions, like when switching views

        // save current search to local storage
        localStorage.setItem("searchItems", JSON.stringify(validSearchItems.value))
        localStorage.setItem("version", config.version)
        lastSearchSettings.value = structuredClone(toRaw(searchSettings.value))

        // set them as url params
        setSearchParamsInUrl()
        // set window title, but only if we are not on the trends page
        if (router.currentRoute.value.name != "trends")
            document.title = `${config.app.name} - ` + validSearchItems.value.map((i) => searchToString(i)).join(", ")

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
        toBeSearched.forEach((ds, idx) => {
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
                setTimeout(() => {
                    // only one search
                    getFrequency(ds)
                }, idx * 150) // space out
            }
        })
        // only show loading screen and send to plausible if we're searching
        if (toBeSearched.length > 0) {
            isSearching.value = true
            plausibleWordsEvent("zoeken", searchSettings.value, validSearchItems.value)
        }
    }
    function getFrequency(item: SearchItem) {
        // construct search request, partly from unsanitized user input
        const searchRequest: SearchAPI.SearchRequest = {
            // unsanitized user input
            w: termPropToString(item, "wordform"),
            l: termPropToString(item, "lemma"),
            p: termPropToString(item, "pos"),
            // fixed values
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
                        abs: res.data.map((i) => ({ x: i[0] * 1000, y: i[1] })),
                        rel: res.data.map((i) => ({ x: i[0] * 1000, y: i[2] })),
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
        const itemStrs: string[] | undefined = items.map((i) => i[prop] || undefined)
        return joinItemStrs(itemStrs)
    }
    function searchTermToUrlStr(items: SearchItem[], prop: string): string | undefined {
        const itemStrs = items.map((i) => termPropToString(i, prop)?.replace(/,/g, "%2C"))
        return joinItemStrs(itemStrs)
    }

    function joinItemStrs(itemStrs: string[]) {
        return itemStrs.every((i) => !i) ? undefined : itemStrs.join(",")
    }

    function setSearchParamsInUrl() {
        const paramsObj = {
            w: searchTermToUrlStr(validSearchItems.value, "wordform"),
            l: searchTermToUrlStr(validSearchItems.value, "lemma"),
            p: searchTermToUrlStr(validSearchItems.value, "pos"),
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
        router.push({ query: { ...router.currentRoute.value.query, ...paramsObj }, replace: true })
    }
    // Lifecycle
    /** ensure that color and visibility updates to search items also update the result items */
    watch(
        () => validSearchItems.value,
        () => {
            // for each search item, try to find the corresponding search result (using equalSearchItem())
            searchResults.value.forEach((result) => {
                // find the corresponding search item
                const searchItem = validSearchItems.value.find(
                    (item: SearchItem) => item.uuid === result.searchItem.uuid,
                )
                // if found, update the color and visibility
                if (searchItem) {
                    result.searchItem.visible = searchItem.visible
                    // language split overrides color
                    if (!lastSearchSettings.value?.languageSplit) {
                        result.searchItem.color = searchItem.color
                    }
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
