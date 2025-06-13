// Types
import { displayName, type GraphItem } from "@/types/search"

export function firstTruthyWord(words: GraphItem[]): string | null {
    return words.map((i) => displayName(i.searchItem)).find((i) => i) || null
}

export function getFileName(words: GraphItem[]): string {
    const word = firstTruthyWord(words)
    return word ? `woordpeiler_${word}_${dateTimeStamp()}.png` : `woordpeiler_${dateTimeStamp()}.png`
}

function dateTimeStamp(): string {
    const now = new Date()
    const date = now.toLocaleDateString()
    const time = now.toLocaleTimeString()
    return `${date}T${time}`.replace(/:/g, "_") // colons not allowed in filenames
}
