export type TrendSettings = {
    year: DateRange;
    month: DateRange;
    week: DateRange;
    other: DateRange;
    trendType: string;
    modifier: number;
    period: string;

export type DateRange = {
    start: Date;
    end: Date;
}

export type TrendResult = {
    keyness: number;
    poshead: string;
    pos: string;
    lemma: string;
    wordform: string;
}
