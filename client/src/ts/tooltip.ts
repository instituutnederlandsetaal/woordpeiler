// Libraries
import * as d3 from "d3"
// Types
import { displayName, type GraphItem, type SearchSettings } from "@/types/search"
// Utils
import { constructTooltipLink } from "@/ts/blacklab/blacklab"

export function tooltipHtml(point: GraphItem, settings: SearchSettings): string {
    const name = displayName(point.searchItem).split("–")[0]
    let language_or_source
    if (point.searchItem.language) {
        language_or_source = point.searchItem.language
    } else if (point.searchItem.source) {
        language_or_source = point.searchItem.source
    }
    let source
    if (language_or_source) {
        source = `<br><small>${language_or_source}</small>`
    } else {
        source = ""
    }

    const date = d3.timeFormat("%Y-%m-%d")(point.x)
    const abs_or_rel = settings.frequencyType == "abs_freq" ? "voorkomens" : "/ mln. woorden"
    const value = `${truncateRound(point.y, 2).toLocaleString()} <small>${abs_or_rel}</small>`
    const href = constructTooltipLink(point, settings)
    const a = containsMath(name) ? "" : `<a target='_blank' href='${href}'>Zoeken in Couranten</a>`

    return `<b>${name}</b>${source}<br>${date}<br><b>${value}</b><br/>${a}`
}

// round e.g. 1.4999 to 1.49 at decimals=2
function truncateRound(value: number, decimals: number) {
    const scaledFloat = value * Math.pow(10, decimals)
    const integerPart = Math.floor(scaledFloat)
    const truncated = integerPart / Math.pow(10, decimals)
    return truncated
}

function containsMath(s: string) {
    return s.includes("/") || s.includes("+")
}
