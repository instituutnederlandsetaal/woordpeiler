export type SpotlightSection = {
    title?: string
    content?: string[]
    blocks: SpotlightBlock[]
}

export type SpotlightBlock = {
    title: string
    subtitle?: string
    articleUrl?: string
    color: string
    graph?: SpotlightGraph
    content?: string[]
}

export type SpotlightGraph = {
    word?: string
    lemma?: string
    start: string
    interval: string
}
