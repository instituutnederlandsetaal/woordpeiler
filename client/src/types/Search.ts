export type SearchSettings = {
    timeBucketType: string;
    timeBucketSize: number;
    startDate: Date;
    endDate: Date;
    frequencyType: string;
}

export interface SearchItem {
    wordform?: string
    pos?: string
    lemma?: string
    newspaper?: string
    language?: string
    color?: string
    visible?: boolean
    loading?: boolean
}

export function equalSearchItem(a: SearchItem, b: SearchItem): boolean {
    return a.wordform === b.wordform &&
        a.pos === b.pos &&
        a.lemma === b.lemma &&
        a.newspaper === b.newspaper &&
        a.language === b.language;
}

export function displayName(i: SearchItem): string {
    return `${i.wordform || ""} ${i.lemma || ""} ${i.pos || ""} ${i.newspaper || ""} ${i.language || ""}`.trim()
}

export function invalidInputText(text?: string): boolean {
    return text?.trim().includes(" ") === true
}

export function invalidSearchItem(item: SearchItem): boolean {
    return displayName(item).trim() == "" || invalidInputText(item.lemma)
}

export type TimeSeries = {
    x: number;
    y: number;
}

export type GraphItem = {
    searchItem: SearchItem;
    data: TimeSeries[];
    uuid: string;
}

