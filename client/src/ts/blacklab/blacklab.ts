import { type SearchItem } from "@/types/search"
import { type GraphItem } from "@/types/graph"
import { type SearchSettings, IntervalType } from "@/types/searchSettings"
import * as d3 from "d3"
import { config } from "@/main"
import type { SearchTerm } from "@/types/searchTerm"

export function constructSearchLink(item: SearchItem, settings: SearchSettings): string {
    // group on year or year-month
    let group
    if (settings.intervalType == IntervalType.YEAR) {
        group = `field:${config.blacklab.grouping.year}:i`
    } else if (settings.intervalType == IntervalType.MONTH) {
        group = `field:${config.blacklab.grouping.year}:i,field:${config.blacklab.grouping.month}:i`
    } else {
        // week or day
        group = `field:${config.blacklab.grouping.year}:i,field:${config.blacklab.grouping.month}:i,field:${config.blacklab.grouping.day}:i`
    }

    // optionally filter on language
    const filterObj = { settingLocation_country: item.language, titleLevel2: item.source }
    const filter =
        Object.entries(filterObj)
            .filter((i) => i[1])
            .map(([key, value]) => `${key}:"${value}"`)
            .join(" AND ") || null

    const params = {
        patt: constructBLPatt(item),
        interface: JSON.stringify({ form: "search", patternMode: "expert" }),
        groupDisplayMode: "hits",
        group: group,
        sort: "-identity",
    }
    if (filter) {
        params["filter"] = filter
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
        group: `field:${config.blacklab.title}:i`,
    }
    const base = getBaseURL()

    return `${base}?${new URLSearchParams(params).toString()}`
}

function getBaseURL(): string {
    return config.internal ? config.blacklab.url.internal : config.blacklab.url.external
}

function constructBLPatt(item: SearchItem) {
    // blacklab pattern format:
    // [word=l"hello" & pos=l"int"][lemma=l"world"]
    // Or without 'l' if regex:
    return item.terms.map(constructSingleBLPatt).join("")
}

function constructSingleBLPatt(term: SearchTerm): string {
    const wordform = constructSingleBLPattProp(term, "wordform", "word")
    const lemma = constructSingleBLPattProp(term, "lemma", "lemma")
    const pos = constructSingleBLPattProp(term, "pos", "pos")

    const patt = [wordform, lemma, pos].filter(Boolean).join("&")
    return `[${patt}]`
}

function constructSingleBLPattProp(term: SearchTerm, prop: string, blName: string): string | undefined {
    const propValue = term[prop as keyof SearchTerm]
    if (!propValue) return undefined
    const isRegex = propValue.includes("*") || propValue.includes("?")
    const literal = isRegex ? "" : "l"
    const value = isRegex ? toBLRegex(propValue) : propValue
    return `${blName}=${literal}"${value}"`
}

function toBLRegex(s: string): string {
    return s.replace(/\*/g, ".*").replace(/\?/g, ".")
}

function constructBLFilter(point: GraphItem, settings: SearchSettings) {
    let filters = {}
    if (config.blacklab.filter) {
        filters = structuredClone(config.blacklab.filter)
    }
    const bucketType = settings.intervalType
    const bucketSize = settings.intervalLength
    const year: number = parseInt(d3.timeFormat("%Y")(point.x))
    const month: number = parseInt(d3.timeFormat("%m")(point.x))
    const day: number = parseInt(d3.timeFormat("%d")(point.x))

    const start = d3.timeFormat("%Y%m%d")(point.x)
    let end
    // end depends on the bucket type and size.
    if (bucketType == IntervalType.YEAR) {
        // end is the last day of the year
        end = d3.timeFormat("%Y%m%d")(new Date(year + bucketSize - 1, 11, 31))
    } else if (bucketType == IntervalType.MONTH) {
        // end is the last day of the month
        end = d3.timeFormat("%Y%m%d")(new Date(year, month + bucketSize - 1, 0))
    } else if (bucketType == IntervalType.WEEK) {
        // weekEnd is 6 days later, inclusive. Not 7 days later, because that is the start of the next data point.
        const offset = bucketSize * 7 - 1
        end = d3.timeFormat("%Y%m%d")(d3.timeDay.offset(point.x, offset))
    } else if (bucketType == IntervalType.DAY) {
        // end is the last day of the period defined by the bucket size
        const offset = bucketSize - 1
        end = d3.timeFormat("%Y%m%d")(d3.timeDay.offset(point.x, offset))
    }
    const dateRange = `[${start} TO ${end}]`
    const dateFilter = `(${config.blacklab.date.from}:${dateRange} AND ${config.blacklab.date.to}:${dateRange})`

    if (point.searchItem.source) {
        filters[config.blacklab.title] = `"${point.searchItem.source}"`
    }

    if (point.searchItem.language) {
        filters[config.blacklab.language] = `"${point.searchItem.language}"`
    }

    const otherFilters = Object.entries(filters)
        .map(([key, value]) => `${key}:${value}`)
        .join(" AND ")
    return [dateFilter, otherFilters].filter((i) => i).join(" AND ")
}
