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
    // Also log all words on screen
    const allWords = searchItems.map((i) => i.wordform || "").join(",")
    window.plausible(goal, { props: { "words": allWords } })
}