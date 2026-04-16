import { searchToString } from "@/types/search"
import type { GraphItem } from "@/types/graph"

export function getFileName(words: GraphItem[], ext: string = "png"): string {
    const word = firstTruthyWord(words)
    return word ? `woordpeiler_${word}_${dateTimeStamp()}.${ext}` : `woordpeiler_${dateTimeStamp()}.${ext}`
}

function firstTruthyWord(words: GraphItem[]): string | null {
    return words.map((i) => searchToString(i.searchItem)).find((i) => i) || null
}

function dateTimeStamp(): string {
    const now = new Date()
    const iso = now.toISOString().split(".")[0] // format: 2021-01-01T12:00:00
    return iso.replace(/:/g, "_") // colons not allowed in filenames
}
