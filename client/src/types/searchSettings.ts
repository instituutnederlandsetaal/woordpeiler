export enum IntervalType {
    DAY = "d",
    WEEK = "w",
    MONTH = "m",
    YEAR = "y",
}

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
