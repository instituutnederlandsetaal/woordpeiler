import { saveAs } from 'file-saver'
import { svgString2Image } from "@/ts/svg/conversion"
import type { GraphItem, SearchSettings } from '@/types/Search'
import { getFileName } from '@/ts/svg/filename'
import { plausibleWordsEvent } from '@/ts/plausible'

export function download(resizeState, words: GraphItem[], searchSettings: SearchSettings) {
    const fileName = getFileName(words)
    svgString2Image(resizeState, 'png', callback)

    function callback(dataBlob, filesize) {
        saveAs(dataBlob, fileName) // FileSaver.js function
    }

    // register plausible event
    const searchItems = words.map((i) => i.searchItem)
    plausibleWordsEvent("download", searchSettings, searchItems)
}