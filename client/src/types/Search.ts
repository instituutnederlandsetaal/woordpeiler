export type SearchSettings = {
    timeBucketType: string;
    timeBucketSize: number;
    startDate: Date;
    endDate: Date;
    frequencyType: string;

export function equalSearchSettings(a: SearchSettings, b: SearchSettings): boolean {
    return a.timeBucketType == b.timeBucketType &&
        a.timeBucketSize == b.timeBucketSize &&
        new Date(a.startDate).toISOString() == new Date(b.startDate).toISOString() &&
        new Date(a.endDate).toISOString() == new Date(b.endDate).toISOString()
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
    return a.wordform == b.wordform &&
        a.pos == b.pos &&
        a.lemma == b.lemma &&
        a.source == b.source &&
        a.language == b.language;
}

export function displayName(i: SearchItem): string {
    let attrs = {
        wordform: i.wordform,
        lemma: i.lemma ? `‘${i.lemma}’` : undefined,
        pos: i.pos,
        source: i.source,
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
    if (displayName(item) == "") {
        // An empty item is invalid
        return true
    } else { // not empty
        // no spaces in lemma
        if (invalidInputText(item.lemma)) {
            return true // invalid
        }
        // language and source can't be both defined
        if (item.language && item.source) {
            return true // invalid
        }
    }
    return false // not invalid
}

export type TimeSeries = {
    x: number;
    y: number;
}

export type TimeSeriesWrapper = {
    abs_freq: TimeSeries[];
    rel_freq: TimeSeries[];
}

export type GraphItem = {
    searchItem: SearchItem;
    data: TimeSeriesWrapper;
    uuid: string;
}

