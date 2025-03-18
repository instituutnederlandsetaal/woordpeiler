// Libraries & Stores
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
// Types & API
import type { SelectLabel } from '@/types/UI'
import { displayName, invalidSearchItem, type SearchItem } from '@/types/Search'
import * as ListingAPI from '@/api/listing'
import { randomColor } from '@/ts/color'
import { isInternal } from '@/ts/internal'

/**
 * Used to manage the list of words that will be used as search items when querying frequency data.
 * Requires fetchOptions to populate the Select options.
 */
export const useSearchItemsStore = defineStore('SearchItems', () => {
    // Fields
    const searchItems = ref<SearchItem[]>([{ color: randomColor(), visible: true }])
    const validSearchItems = computed<SearchItem[]>(() => searchItems.value.filter((i) => !invalidSearchItem(i)))
    /** Source options, to be fetched */
    const sourceOptions = ref<string[]>([])
    /** Part of Speech options, to be fetched */
    const posOptions = ref([])
    const languageOptions = ref<string[]>([])
    // computed
    const isValid = computed<Boolean>(() => {
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
    /** Fetch all unique sources and parts of speech */
    async function fetchOptions() {
        if (!isInternal()) return

        // Dont keep refetching
        if (sourceOptions.value.length > 0 && posOptions.value.length > 0) {
            return
        }

        ListingAPI.getLanguages()
            .then((response) => {
                languageOptions.value = response.data
            })

        ListingAPI.getSources()
            .then((response) => {
                sourceOptions.value = response.data
            })

        let posses: string[] = []
        await ListingAPI.getPosses()
            .then((response) => {
                posses = response.data
            })

        let posHeads: string[] = []
        await ListingAPI.getPosheads()
            .then((response) => {
                posHeads = response.data
            })

        posOptions.value = transformPos(posses, posHeads)
    }
    /** Transform the pos and poshead listing into a combined object, grouped by poshead */
    function transformPos(posses: string[], posHeads: string[]) {
        // posses is now in the form [NOU(num=sg), NOU(num=pl), AA, ...]
        // We want to transform this into [{label: "NOU", items: [{label: "NOU(num=sg)", value: "NOU(num=sg)"}]}, {label: "AA", items: ...]}, ...]
        return posHeads.filter(posHead => !["punct", "__eos__"].includes(posHead)).map((posHead) => {
            return {
                label: posHead,
                items: [posHead].concat(posses.filter((pos) => pos.startsWith(posHead) && pos.includes("(") && !pos.includes("()")).map((pos) => {
                    return pos
                }))
            }

        })
    }
    function readURLParams() {
        const split = ","

        const urlParams = new URLSearchParams(window.location.search)
        const words = urlParams.get('w')
        const lemmas = urlParams.get('l')
        const pos = urlParams.get('p')
        const source = urlParams.get('s')
        const language = urlParams.get('v')
        const color = urlParams.get('c')
        const range = [...Array(Math.max(words?.split(split).length || 0, lemmas?.split(split).length || 0, pos?.split(split).length || 0, source?.split(split).length || 0, language?.split(split).length || 0)).keys()]

        try {
            if (range.length > 0) {
                searchItems.value = range.map((i) => {
                    return {
                        wordform: words?.split(split)[i] || undefined,
                        lemma: lemmas?.split(split)[i] || undefined,
                        pos: pos?.split(split)[i] || undefined,
                        source: source?.split(split)[i] || undefined,
                        language: language?.split(split)[i].toUpperCase() || undefined,
                        color: color?.split(split)[i] || randomColor(),
                        visible: true
                    }
                })
            }
        } catch (e) {
            searchItems.value = [{ color: randomColor(), visible: true }]
        }
    }
    // Export
    return {
        // Fields
        searchItems, sourceOptions, languageOptions, posOptions, isValid, validSearchItems,
        // Methods
        fetchOptions, readURLParams
    }
})