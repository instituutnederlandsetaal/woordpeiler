import type { SearchItem, SearchSettings } from "@/types/Search"

export function plausibleWordsEvent(goal: string, searchSettings: SearchSettings, searchItems: SearchItem[]) {
    // each word individually
    searchItems.forEach((i) => {
        const wordLower = i.wordform?.toLowerCase()

        const props: Record<string, string | undefined> = { "word": wordLower }
        // if a language is set, add it to the props
        if (i.language) {
            props[`${i.language}-word`] = wordLower
        } else if (searchSettings.languageSplit) {
            props["ALL-LANG-word"] = wordLower
        }
        window.plausible(goal, { props })
    })

    // Also log all words when more than one word is shown
    // So we can see which words are searched together
    const wordforms = searchItems.map((i) => i.wordform || "")
    if (wordforms.length > 1) {
        const wordsCommaList = wordforms.join(",")
        window.plausible(goal, { props: { "words": wordsCommaList } })
    }
}