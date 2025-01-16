import { displayName, type GraphItem } from "@/types/Search"
import { svgString2Image } from "@/ts/svg/conversion"
import { getFileName } from "@/ts/svg/filename"

export function share(resizeState, words: GraphItem[]) {
    // choose first truthy display name or null
    const word: string | null = words.map((i) => displayName(i.searchItem)).find((i) => i) || null

    if (canShareFiles()) {
        shareImage(resizeState, words)
    } else {
        shareLink(word)
    }

    // register plausible event
    window.plausible("share")
}

function canShareFiles(): boolean {
    return navigator.canShare({ files: [new File([], '')] })
}

function shareImage(resizeState: any, words: GraphItem[]) {
    const fileName = getFileName(words)
    svgString2Image(resizeState, 'png', callback)
    function callback(dataBlob, filesize) {
        const file = new File([dataBlob], fileName, { type: 'image/png' })
        navigator.share({ files: [file], title: "Woordpeiler" })
    }
}

function shareLink(word: string | null) {
    const url = window.location.href
    const text = word ? `het woord "${word}"` : "woordtrends"
    navigator.share({
        title: "Woordpeiler",
        text: `Bekijk ${text} op Woordpeiler: ${url}`,
    })
}
