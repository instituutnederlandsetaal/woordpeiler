import { config } from "@/main"

export enum IntervalType {
    DAY = "d",
    WEEK = "w",
    MONTH = "m",
    YEAR = "y",
}

export const intervalMap = { d: "day", w: "week", m: "month", y: "year" }

/** converts 1 month to 1m */
export function toIntervalStr(period_type: string, period_length: number): string {
    return period_length + period_type[0]
}

export type SearchSettings = {
    intervalType: string
    intervalLength: number
    startDate: Date
    endDate: Date
    frequencyType: string
    languageSplit: boolean
}

export function equalSearchSettings(a: SearchSettings, b: SearchSettings): boolean {
    return (
        a.languageSplit == b.languageSplit &&
        a.intervalType == b.intervalType &&
        a.intervalLength == b.intervalLength &&
        a.startDate.getTime() == b.startDate.getTime() &&
        a.endDate.getTime() == b.endDate.getTime()
    )
}

export interface SearchItem {
    wordform?: string
    pos?: string
    lemma?: string
    source?: string
    language?: string
    color?: string
    visible?: boolean
    loading?: boolean
}

export function equalSearchItem(a: SearchItem, b: SearchItem): boolean {
    return (
        a.wordform == b.wordform &&
        a.pos == b.pos &&
        a.lemma == b.lemma &&
        a.source == b.source &&
        a.language == b.language
    )
}

export function displayName(i: SearchItem): string {
    const attrs = {
        wordform: i.wordform,
        lemma: i.lemma ? `‘${i.lemma}’` : undefined,
        pos: i.pos,
        source: i.source,
        language: i.language,
    }
    const cleanedAttrs: string[] = Object.values(attrs)
        .map((v) => v?.trim())
        .filter((v) => v != undefined)
        .filter((v) => v != "")
    const nDash = "–"
    return cleanedAttrs.join(nDash)
}

export function invalidInputText(text?: string): boolean {
    const num_words = text?.trim().split(" ").length ?? 0
    return num_words > config.searchItems.ngram // 5-grams not supported
}

export function invalidRegexUsage(text?: string): boolean {
    // regex only allowed with at least 4 characters
    if (text && text.includes("*")) {
        if (text.replaceAll("*", "").length < 4) {
            return true // invalid
        }
    }
    return false // not invalid
}

export function invalidSearchItem(item: SearchItem): boolean {
    if (displayName(item) == "") {
        // An empty item is invalid
        return true
    } else {
        // not empty
        // check ngram length and regex usage
        if (
            invalidInputText(item.lemma) ||
            invalidInputText(item.wordform) ||
            invalidRegexUsage(item.lemma) ||
            invalidRegexUsage(item.wordform)
        ) {
            return true // invalid
        }
    }
    return false // not invalid
}

export type TimeSeries = { x: number; y: number }

export type TimeSeriesWrapper = { abs_freq: TimeSeries[]; rel_freq: TimeSeries[] }

export type GraphItem = { searchItem: SearchItem; data: TimeSeriesWrapper; uuid: string }
