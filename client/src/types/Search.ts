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
    variant?: string
}

export type TimeSeries = {
    x: number;
    y: number;
}

export type GraphItem = {
    datapoint: SearchItem;
    data: TimeSeries[];
    label: string;
    borderColor: string;
    backgroundColor: string;
}

