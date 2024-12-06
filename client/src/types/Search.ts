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
    let attrs = {
        wordform: i.wordform,
        lemma: i.lemma,
        pos: i.pos,
        newspaper: i.newspaper,
        language: i.language
    }
    const cleanedAttrs: String[] = Object.values(attrs).map(v => v?.trim()).filter(v => v != undefined).filter(v => v != "")
    const nDash = "–"
    return cleanedAttrs.join(nDash)
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

