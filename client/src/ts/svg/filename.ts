import { searchToString } from "@/types/search"
import type { GraphItem } from "@/types/graph"

export function getFileName(words: GraphItem[]): string {
    const word = firstTruthyWord(words)
    return word ? `woordpeiler_${word}_${dateTimeStamp()}.png` : `woordpeiler_${dateTimeStamp()}.png`
}

function firstTruthyWord(words: GraphItem[]): string | null {
    return words.map((i) => searchToString(i.searchItem)).find((i) => i) || null
}

function dateTimeStamp(): string {
    const now = new Date()
    const date = now.toLocaleDateString()
    const time = now.toLocaleTimeString()
    return `${date}T${time}`.replace(/:/g, "_") // colons not allowed in filenames
}
