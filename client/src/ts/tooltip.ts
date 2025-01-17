import * as d3 from "d3";
import { displayName, type GraphItem, type SearchItem, type SearchSettings } from "@/types/Search";
import { isInternal } from "@/ts/internal";



export function tooltipHtml(point: GraphItem, settings: SearchSettings): string {
    const name = displayName(point.searchItem).split("–")[0];
    let language_or_source;
    if (point.searchItem.language) {
        const langMap = {
            "AN": "Antilliaans-Nederlands",
            "BN": "Belgisch-Nederlands",
            "NN": "Nederlands-Nederlands",
            "SN": "Surinaams-Nederlands",
        }
        language_or_source = langMap[point.searchItem.language]
    } else if (point.searchItem.source) {
        language_or_source = point.searchItem.source
    }
    let source;
    if (language_or_source) {
        source = `<br><small>${language_or_source}</small>`
    } else {
        source = ""
    }


    const date = d3.timeFormat("%Y-%m-%d")(point.x);
    const abs_or_rel = settings.frequencyType == "abs_freq" ? "voorkomens" : "/ mln. woorden";
    const value = `${truncateRound(point.y, 2).toLocaleString()} <small>${abs_or_rel}</small>`;
    const href = constructBlLink(point, settings);
    const a = containsMath(name) ? '' : `<a target='_blank' href='${href}'>Zoeken in CHN</a>`

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

/** Construct a BlackLab link for the wordform*/
function constructBlLink(point: GraphItem, settings: SearchSettings): string {
    const params = {
        patt: constructBLPatt(point.searchItem),
        filter: constructBLFilter(point, settings),
        interface: JSON.stringify({ form: "search", patternMode: "expert" }),
        groupDisplayMode: "relative hits",
        group: "field:titleLevel2:i"
    }
    const internalBase = "http://svotmc10.ivdnt.loc:8080/corpus-frontend/chn-intern/search/hits"
    const externalBase = "https://portal.clarin.ivdnt.org/corpus-frontend-chn/chn-extern/search/hits"
    const base = isInternal() ? internalBase : externalBase;

    return `${base}?${new URLSearchParams(params).toString()}`
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