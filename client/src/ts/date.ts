export function toTimestamp(date: Date): string {
    // format: 2021-01-01
    return date.toISOString().slice(0, 10)
}

export function toUTCDate(date: Date): Date {
    const localYear = date.getFullYear()
    const localMonth = date.getMonth()
    const localDay = date.getDate()
    return new Date(Date.UTC(localYear, localMonth, localDay))
}

export function toMidnightUTC(timestamp: number): number {
    const d = new Date(timestamp * 1000)
    const midnight_utc = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 1000
    return midnight_utc
}

export function getNewYearsDay(): Date {
    const now = new Date()
    return new Date(now.getFullYear(), 0, 1)
}
export function getNewYearsEve(): Date {
    const now = new Date()
    return new Date(now.getFullYear(), 11, 31)
}

export function toLastDayOfYear(date: Date): Date {
    return new Date(date.getFullYear(), 11, 31)
}

export function toLastDayOfMonth(date: Date): Date {
    // bit trickier because months are different lengths
    const nextMonth = new Date(date.getFullYear(), date.getMonth() + 1, 1)
    return new Date(nextMonth.getFullYear(), nextMonth.getMonth(), 0)
}

export function toFirstDayOfMonth(date: Date): Date {
    return new Date(date.getFullYear(), date.getMonth(), 1)
}

/** For a given date, get the ISO week number
 *
 * Based on information at:
 *
 *    THIS PAGE (DOMAIN EVEN) DOESN'T EXIST ANYMORE UNFORTUNATELY
 *    http://www.merlyn.demon.co.uk/weekcalc.htm#WNR
 *
 * Algorithm is to find nearest thursday, it's year
 * is the year of the week number. Then get weeks
 * between that date and the first day of that year.
 *
 * Note that dates in one year can be weeks of previous
 * or next year, overlap is up to 3 days.
 *
 * e.g. 2014/12/29 is Monday in week  1 of 2015
 *      2012/1/1   is Sunday in week 52 of 2011
 */
// https://stackoverflow.com/a/6117889/
function getWeekNumber(d) {
    // Copy date so don't modify original
    d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
    // Set to nearest Thursday: current date + 4 - current day number
    // Make Sunday's day number 7
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7))
    // Get first day of year
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
    // Calculate full weeks to nearest Thursday
    const weekNo = Math.ceil(((d - yearStart) / 86400000 + 1) / 7)
    // Return array of year and week number
    return [d.getUTCFullYear(), weekNo]
}
