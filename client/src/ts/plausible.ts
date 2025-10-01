import { searchToString, type SearchItem } from "@/types/search"
import { toIntervalStr, type SearchSettings } from "@/types/searchSettings"
import { toTimestamp } from "@/ts/date"

declare global {
    interface Window {
        plausible: (eventName: string, props?: Record<string, any>) => void
    }
}

// debug printing for plausible
if (location.hostname.includes("localhost")) {
    window.plausible = (eventName: string, props?: Record<string, any>): void =>
        console.log(`localhost plausible event: ${eventName}\nparams: ${JSON.stringify(props)}`)
}

export function plausibleWordsEvent(goal: string, settings: SearchSettings, items: SearchItem[]) {
    const props = {
        query: items
            .map((i) => searchToString(i)?.toLowerCase())
            .sort()
            .join(","),
        word: items.some((item: SearchItem) => item.terms?.some((t) => Boolean(t.wordform))),
        lemma: items.some((item: SearchItem) => item.terms?.some((t) => Boolean(t.lemma))),
        pos: items.some((item: SearchItem) => item.terms?.some((t) => Boolean(t.pos))),
        sources: [...new Set(items.map((i) => i.source?.toLowerCase()).filter(Boolean))].sort().join(",") || undefined,
        langs: [...new Set(items.map((i) => i.language?.toLowerCase()).filter(Boolean))].sort().join(",") || undefined,
        interval: toIntervalStr(settings.intervalType, settings.intervalLength),
        start: toTimestamp(settings.startDate),
        end: toTimestamp(settings.endDate),
        freq: settings.frequencyType,
        langSplit: settings.languageSplit,
    }
    window.plausible(goal, { props })
}

export function plausibleCorpus(type: "tooltip" | "legend" | "searchterm") {
    window.plausible("corpus", { props: { type } })
}
