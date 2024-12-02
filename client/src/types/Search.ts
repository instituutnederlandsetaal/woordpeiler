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
}

export function equalSearchItem(a: SearchItem, b: SearchItem): boolean {
    return a.wordform === b.wordform &&
        a.pos === b.pos &&
        a.lemma === b.lemma &&
        a.newspaper === b.newspaper &&
        a.language === b.language;
}

export type TimeSeries = {
    x: number;
    y: number;
}

export type GraphItem = {
    datapoint: SearchItem;
    data: TimeSeries[];
    label: string;
}

