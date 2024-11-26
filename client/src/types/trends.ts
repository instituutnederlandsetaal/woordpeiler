export type TrendSettings = {
    periodType: string;
    periodLength: number;
    trendType: string;
    modifier: number;
}

export type TrendResult = {
    keyness: number;
    poshead: string;
    wordform: string;
}
