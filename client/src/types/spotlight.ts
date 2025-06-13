export type Spotlight = {
    title?: string
    articleUrl?: string
    word?: string
    lemma?: string
    color: string
    start: string
    interval: string
    // legacy
    start_date?: string
    period_type?: string
    period_length?: number
}
