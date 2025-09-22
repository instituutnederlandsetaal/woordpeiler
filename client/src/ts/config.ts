export type Config = {
    basePath: string
    internal: boolean
    version: string
    spotlights: { url: string; default: string }
    app: { name: string; slogan: string; description: string }
    search: {
        ngram: number
        interval: { desktop: { type: string; size: number }; mobile: { type: string; size: number } }
        filters: { name: string; api: string; advanced: boolean }[]
        autosplit: { on: string; colors: Record<string, string> }
    }
    tagset: Record<string, string>
    language: Record<string, string>
    corpus: { name: string; url: string }
    period: { start: string }
    theme: { color: string; logo: string; favicon: string }
    blacklab: {
        url: { external: string; internal: string }
        filter: { medium: string }
        annotations: { word: string; lemma: string; pos: string; poshead: string }
        grouping: { year: string; month: string; day: string }
        date: string[]
        title: string
        language: string
    }
}
