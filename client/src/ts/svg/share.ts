// Types
import { searchToString } from "@/types/search"
import type { GraphItem } from "@/types/graph"
import { type SearchSettings } from "@/types/SearchSettings"
import type { ResizeState } from "@/ts/resizeObserver"
// Utils
import { svgString2Image } from "@/ts/svg/conversion"
import { getFileName } from "@/ts/svg/filename"
import { plausibleWordsEvent } from "@/ts/plausible"

export function share(resizeState: ResizeState, words: GraphItem[], searchSettings: SearchSettings) {
    // choose first truthy display name or null
    const word: string | null = words.map((i) => searchToString(i.searchItem)).find((i) => i) || null

    if (canShareFiles()) {
        shareImage(resizeState, words)
    } else {
        shareLink(word)
    }

    // register plausible event
    const searchItems = words.map((i) => i.searchItem)
    plausibleWordsEvent("share", searchSettings, searchItems)
}

function canShareFiles(): boolean {
    return navigator.canShare({ files: [new File([], "")] })
}

function shareImage(resizeState: ResizeState, words: GraphItem[]) {
    const fileName = getFileName(words)
    svgString2Image(resizeState, callback)
    function callback(dataBlob, _filesize) {
        const file = new File([dataBlob], fileName, { type: "image/png" })
        navigator.share({ files: [file], title: "Woordpeiler" })
    }
}

function shareLink(word: string | null) {
    const url = window.location.href
    const text = word ? `het woord "${word}"` : "woordtrends"
    navigator.share({ title: "Woordpeiler", text: `Bekijk ${text} op Woordpeiler: ${url}` })
}
