// Types & API
import { displayName, invalidSearchItem, type SearchItem } from "@/types/search"
import { randomColor } from "@/ts/color"

/**
 * Used to manage the list of words that will be used as search items when querying frequency data.
 * Requires fetchOptions to populate the Select options.
 */
export const useSearchItemsStore = defineStore("SearchItems", () => {
    // Fields
    const searchItems = ref<SearchItem[]>([{ color: randomColor(), visible: true }])
    const validSearchItems = computed<SearchItem[]>(() => searchItems.value.filter((i) => !invalidSearchItem(i)))
    // computed
    const isValid = computed<boolean>(() => {
        // empty array
        if (searchItems.value.length === 0) {
            return false
        }
        // single empty item
        if (searchItems.value.length == 1) {
            return !invalidSearchItem(searchItems.value[0])
        }
        // Check every term
        for (const i of searchItems.value) {
            if (displayName(i) == "") {
                // If it is completely empty, that's fine.
            } else {
                if (invalidSearchItem(i)) {
                    return false
                }
            }
        }
        return true
    })
    // Methods
    function readURLParams() {
        const split = ","

        const urlParams = new URLSearchParams(window.location.search)
        const words = urlParams.get("w")
        const lemmas = urlParams.get("l")
        const pos = urlParams.get("p")
        const source = urlParams.get("s")
        const language = urlParams.get("v")
        const color = urlParams.get("c")
        const range = [
            ...Array(
                Math.max(
                    words?.split(split).length || 0,
                    lemmas?.split(split).length || 0,
                    pos?.split(split).length || 0,
                    source?.split(split).length || 0,
                    language?.split(split).length || 0,
                ),
            ).keys(),
        ]

        try {
            if (range.length > 0) {
                searchItems.value = range.map((i) => {
                    return {
                        wordform: words?.split(split)[i] || undefined,
                        lemma: lemmas?.split(split)[i] || undefined,
                        pos: pos?.split(split)[i] || undefined,
                        source: source?.split(split)[i] || undefined,
                        language: language?.split(split)[i] || undefined,
                        color: color?.split(split)[i] || randomColor(),
                        visible: i < 3 ? true : false,
                    }
                })
            }
        } catch {
            searchItems.value = [{ color: randomColor(), visible: true }]
        }
    }
    // Export
    return {
        // Fields
        searchItems,
        isValid,
        validSearchItems,
        // Methods
        readURLParams,
    }
})
