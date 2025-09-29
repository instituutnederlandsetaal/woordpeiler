import { invalidSearchItem, type SearchItem, type SearchTerm } from "@/types/search"
import { randomColor } from "@/ts/color"

/** list of words that will be used as search items when querying frequency data. */
export const useSearchItems = defineStore("searchItems", () => {
    // Fields
    const searchItems = ref<SearchItem[]>([])
    const validSearchItems = computed<SearchItem[]>(() => searchItems.value.filter((i) => !invalidSearchItem(i)))
    // Methods
    function searchItemsFromUrl() {
        const split = ","
        const urlParams = new URLSearchParams(window.location.search)
        const words = urlParams.get("w")
        const lemmas = urlParams.get("l")
        const posses = urlParams.get("p")
        const source = urlParams.get("s")
        const language = urlParams.get("v")
        const colors = urlParams.get("c")
        const numSearchItems = [
            ...Array(
                Math.max(
                    words?.split(split).length || 0,
                    lemmas?.split(split).length || 0,
                    posses?.split(split).length || 0,
                    source?.split(split).length || 0,
                    language?.split(split).length || 0,
                ),
            ).keys(),
        ]
        try {
            if (numSearchItems.length > 0) {
                searchItems.value = numSearchItems.map((i) => {
                    const wordform = words?.split(split)[i] || undefined
                    const lemma = lemmas?.split(split)[i] || undefined
                    const pos = posses?.split(split)[i] || undefined
                    const terms = toTerm(wordform, lemma, pos)
                    return {
                        terms: terms,
                        source: source?.split(split)[i] || undefined,
                        language: language?.split(split)[i] || undefined,
                        color: colors?.split(split)[i] || randomColor(),
                        visible: i < 3 ? true : false,
                        uuid: crypto.randomUUID(),
                    }
                })
            }
        } catch {
            searchItems.value = [{ color: randomColor(), visible: true, uuid: crypto.randomUUID() }]
        }
    }

    function toTerm(wordform?: string, lemma?: string, pos?: string): SearchTerm[] {
        const split = " "
        const ngram = Math.max(
                    wordform?.split(split).length || 0,
                    lemma?.split(split).length || 0,
                    pos?.split(split).length || 0,
                )
        const terms: SearchTerm[] = []
        for (let i = 0; i < ngram; i++) {
            const term: SearchTerm = {
                wordform: getNthTerm(i, wordform || "") || undefined,
                lemma: getNthTerm(i, lemma || "") || undefined,
                pos: getNthTerm(i, pos || "") || undefined,
            }
            terms.push(term)
        }
        return terms
    }

    function getNthTerm(n: number, text: string): string | undefined {
        const terms = text.split(" ")
        const nthText = terms[n] || undefined
        if (nthText === "[]") {
            return undefined
        }
        return nthText
    }

    return { searchItems, validSearchItems, searchItemsFromUrl }
})
