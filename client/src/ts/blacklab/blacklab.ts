import type { GraphItem, SearchSettings, SearchItem } from "@/types/Search";
import { isInternal } from "@/ts/internal";
import * as d3 from "d3";


export function constructSearchLink(item: SearchItem, settings: SearchSettings): string {
    // group on year or year-month
    let group
    if (settings.timeBucketType == "year") {
        group = "field:grouping_year:i"
    } else if (settings.timeBucketType == "month") {
        group = "field:grouping_year:i,field:grouping_month:i"
    } else { // week or day
        group = "field:grouping_year:i,field:grouping_month:i,field:grouping_day:i"
    }

    // optionally filter on language
    let filter = "medium:newspaper"
    if (item.language) {
        filter += ` AND languageVariant:${item.language}`
    }

    const params = {
        patt: constructBLPatt(item),
        interface: JSON.stringify({ form: "search", patternMode: "expert" }),
        groupDisplayMode: "relative hits",
        group: group,
        sort: "-identity",
        filter: filter,
    }
    const base = getBaseURL()

    return `${base}?${new URLSearchParams(params).toString()}`
}

/** Construct a BlackLab link for the wordform*/
export function constructTooltipLink(point: GraphItem, settings: SearchSettings): string {
    const params = {
        patt: constructBLPatt(point.searchItem),
        filter: constructBLFilter(point, settings),
        interface: JSON.stringify({ form: "search", patternMode: "expert" }),
        groupDisplayMode: "relative hits",
        group: "field:titleLevel2:i"
    }
    const base = getBaseURL()

    return `${base}?${new URLSearchParams(params).toString()}`
}

function getBaseURL(): string {
    const internalBase = "http://chn-i.ivdnt.loc/corpus-frontend/chn-intern/search/hits"
    const externalBase = "https://portal.clarin.ivdnt.org/corpus-frontend-chn/chn-extern/search/hits"
    return isInternal() ? internalBase : externalBase;
}

function constructBLPatt(item: SearchItem) {
    const pattTerms = {
        lemma: item.lemma,
        word: item.wordform,
    }
    // Add pos separately because only one can be present
    if (item.pos?.includes("(")) {
        pattTerms["pos_full"] = item.pos
    }
    else {
        pattTerms["pos"] = item.pos
    }

    // Remove falsy values, and blank strings (could be tabs and spaces)
    Object.keys(pattTerms).forEach(
        (key) => (pattTerms[key] == null || pattTerms[key].trim() === "") && delete pattTerms[key]
    )
    const isRegex = item.wordform?.includes("*") || item.wordform?.includes("?")
    if (isRegex) {
        pattTerms["word"] = toBLRegex(item.wordform)
    }
    const literal = (isInternal() && !isRegex) ? "l" : ""
    const patt = Object.entries(pattTerms).map(([key, value]) => `${key}=${literal}"${value}"`).join("&")
    return `[${patt}]`
}

function toBLRegex(s: string): string {
    return s.replace(/\*/g, ".*").replace(/\?/g, ".")
}

function constructBLFilter(point: GraphItem, settings: SearchSettings) {
    const filters = {
        medium: "newspaper",
    }
    const bucketType = settings.timeBucketType;
    const bucketSize = settings.timeBucketSize;
    const year: number = parseInt(d3.timeFormat("%Y")(point.x))
    const month: number = parseInt(d3.timeFormat("%m")(point.x))
    const day: number = parseInt(d3.timeFormat("%d")(point.x))

    const start = d3.timeFormat("%Y%m%d")(point.x)
    let end;
    // end depends on the bucket type and size.
    if (bucketType == "year") {
        // end is the last day of the year
        end = d3.timeFormat("%Y%m%d")(new Date(year + bucketSize - 1, 11, 31))
    } else if (bucketType == "month") {
        // end is the last day of the month
        end = d3.timeFormat("%Y%m%d")(new Date(year, month + bucketSize - 1, 0))
    } else if (bucketType == "week") {
        // weekEnd is 6 days later, inclusive. Not 7 days later, because that is the start of the next data point.
        const offset = bucketSize * 7 - 1
        end = d3.timeFormat("%Y%m%d")(d3.timeDay.offset(point.x, offset))
    } else if (bucketType == "day") {
        // end is the last day of the period defined by the bucket size
        const offset = bucketSize - 1;
        end = d3.timeFormat("%Y%m%d")(d3.timeDay.offset(point.x, offset));
    }
    filters["witnessDate_from"] = `[${start} TO ${end}]`

    if (point.searchItem.source) {
        filters["titleLevel2"] = `"${point.searchItem.source}"`
    }

    if (point.searchItem.language) {
        filters["languageVariant"] = `"${point.searchItem.language}"`
    }

    return Object.entries(filters).map(([key, value]) => `${key}:${value}`).join(" AND ")
}