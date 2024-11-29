export type TrendSettings = {
    startDate: Date;
    endDate: Date;
    trendType: string;
    modifier: number;
}

export type TrendResult = {
    keyness: number;
    poshead: string;
    wordform: string;
}
