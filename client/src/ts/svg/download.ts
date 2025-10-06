// Libraries
import { saveAs } from "file-saver"
// Types
import type { GraphItem } from "@/types/graph"
import { type SearchSettings } from "@/types/searchSettings"
import type { ResizeState } from "@/ts/resizeObserver"
// Utils
import { svgString2Image } from "@/ts/svg/conversion"
import { getFileName } from "@/ts/svg/filename"
import { plausibleWordsEvent } from "@/ts/plausible"

export function download(resizeState: ResizeState, words: GraphItem[], searchSettings: SearchSettings) {
    const fileName = getFileName(words)
    svgString2Image(resizeState, callback)

    function callback(dataBlob, _filesize) {
        saveAs(dataBlob, fileName) // FileSaver.js function
    }

    // register plausible event
    const searchItems = words.map((i) => i.searchItem)
    plausibleWordsEvent("download", searchSettings, searchItems)
}
