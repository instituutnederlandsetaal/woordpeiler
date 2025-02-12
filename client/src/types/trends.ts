export type TrendSettings = {
    year: DateRange;
    month: DateRange;
    week: DateRange;
    other: DateRange;
    trendType: string;
    modifier: number;
    period: string;
    enriched: boolean;
    ascending: boolean;
    language?: string;
    ngram: number;
}

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

/** format: 1 jan 2022 - 7 jan 2022 */
function weekRangeStr(date: DateRange): string {
    const options = { day: 'numeric', month: 'short', year: 'numeric' }
    const format = (date: Date) => date.toLocaleDateString('nl-NL', options)
    return `${format(date.start)} – ${format(date.end)}`
}

export function displayName(settings: TrendSettings) {
    let period
    if (settings.period === 'year') {
        period = settings.year?.start?.getFullYear()
    } else if (settings.period === 'month') {
        // format: januari 2022
        const month = settings.month?.start?.toLocaleDateString('nl-NL', { month: 'long' })
        period = `${month} ${settings.month?.start?.getFullYear()}`
    } else if (settings.period === 'week') {
        period = weekRangeStr(settings.week)
    } else if (settings.period === 'other') {
        period = weekRangeStr(settings.other)
    }


    return `${period} ${settings.language ?? ''}`
}
