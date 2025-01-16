import { saveAs } from 'file-saver'
import { svgString2Image } from "@/ts/svg/conversion"
import type { GraphItem } from '@/types/Search'
import { getFileName } from '@/ts/svg/filename'


export function download(resizeState, words: GraphItem[]) {
    const fileName = getFileName(words)
    svgString2Image(resizeState, 'png', callback)

    function callback(dataBlob, filesize) {
        saveAs(dataBlob, fileName) // FileSaver.js function
    }
}