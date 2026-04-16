// Libraries
import { saveAs } from "file-saver"
// Types
import type { GraphItem } from "@/types/graph"
import { type SearchSettings } from "@/types/searchSettings"
// Utils
import { plausibleWordsEvent } from "@/ts/plausible"
import { searchToString } from "@/types/search"
import { getFileName } from "@/ts/svg/filename"
import { toUTCDate } from "@/ts/date"

function quoteAndEscape(str: string): string {
    return `"${str.replace(/"/g, '""')}"`
}

export function download(searchResults: GraphItem[]) {
    // create csv content
    // we always have a column for time
    // then two columns per word (absolute and relative)
    // for Microsoft Excel, we need to use a BOM and UTF16LE encoding
    const EXCEL_HEADER = `${"\uFEFF"}sep=,\n`
    const header = ["datum"]
    searchResults.forEach((graphItem) => {
        const itemStr = searchToString(graphItem.searchItem)
        header.push(`${itemStr} (rel. freq.)`, `${itemStr} (abs. freq.)`)
    })
    // for the rows, we can use the first time series as the source of time stamps
    const rows = searchResults[0]?.data.abs.map((d, index) => {
        const date = new Date(d.x).toISOString().split("T")[0] // format: 1970-01-01
        const row = [date]
        searchResults.forEach((graphItem) => {
            const relFreq = graphItem.data.rel[index].y
            const absFreq = graphItem.data.abs[index].y
            row.push(relFreq.toLocaleString(undefined, { style: "decimal" }), absFreq.toString())
        })
        return row
    })
    const csvContent =
        EXCEL_HEADER +
        header.map(quoteAndEscape).join(",") +
        "\n" +
        rows.map((row) => row.map(quoteAndEscape).join(",")).join("\n")
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-16le;" })
    const fileName = getFileName(searchResults, "csv")
    saveAs(blob, fileName)
}
