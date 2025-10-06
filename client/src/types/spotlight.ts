export type SpotlightConfig = { version: string; sections: SpotlightSection[] }

export type SpotlightSection = { id?: string; title?: string; content?: string[]; blocks: SpotlightBlock[] }

export type SpotlightBlock = {
    title?: string
    subtitle?: string
    url?: string
    color: string
    content?: string[]
    words?: string[]
    graph?: SpotlightGraph
}

export type SpotlightGraph = { word?: string; lemma?: string; start: string; interval: string }
