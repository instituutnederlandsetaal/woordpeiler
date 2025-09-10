export type SpotlightSection = { title?: string; content?: string[]; blocks: SpotlightBlock[] }

export type SpotlightBlock = {
    title: string
    id: string
    subtitle?: string
    url?: string
    color: string
    content?: string[]
    words?: string[]; 
    graph?: SpotlightGraph
}

export type SpotlightGraph = { word?: string; lemma?: string; start: string; interval: string }
