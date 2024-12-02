// Libraries & Stores
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
// Types & API
import type { SelectLabel } from '@/types/UI'
import type { SearchItem } from '@/types/Search'
import * as ListingAPI from '@/api/listing'

/**
 * Used to manage the list of words that will be used as search items when querying frequency data.
 * Requires fetchOptions to populate the Select options.
 */
export const useSearchItemsStore = defineStore('SearchItems', () => {
    // Fields
    const searchItems = ref<SearchItem[]>([])
    /** Newspaper options, to be fetched */
    const sourceOptions = ref<string[]>([])
    /** Part of Speech options, to be fetched */
    const posOptions = ref([])
    const languageOptions = ref<SelectLabel[]>([
        { label: "Antilliaans-Nederlands", value: "AN" },
        { label: "Belgisch-Nederlands", value: "BN" },
        { label: "Nederlands-Nederlands", value: "NN" },
        { label: "Surinaams-Nederlands", value: "SN" },
    ])
    // computed
    const isValid = computed<Boolean>(() => {
        // empty array
        if (searchItems.value.length === 0) {
            return false
        }
        // Check if every item has at least one field filled in
        for (const i of searchItems.value) {
            const containsAtLeastOne = i.wordform || i.pos || i.lemma || i.newspaper || i.language
            if (!containsAtLeastOne) {
                return false
            }
        }
        return true
    })
    // Methods
    /** Fetch all unique sources and parts of speech */
    async function fetchOptions() {
        ListingAPI.getListing("sources", "source")
            .then((response) => {
                sourceOptions.value = response.data
            })

        let posses: string[] = []
        await ListingAPI.getListing("words", "pos")
            .then((response) => {
                posses = response.data
            })

        let posHeads: string[] = []
        await ListingAPI.getListing("words", "poshead")
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
    // Export
    return {
        // Fields
        searchItems, sourceOptions, languageOptions, posOptions, isValid,
        // Methods
        fetchOptions
    }
})