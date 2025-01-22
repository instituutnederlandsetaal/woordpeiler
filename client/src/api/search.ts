import axios, { type AxiosResponse } from "axios"
import { cleanParams } from "@/api/api"
import { toMidnightUTC } from "@/ts/date"

export type SearchRequest = {
    id?: number;
    wordform?: string;
    lemma?: string;
    pos?: string;
    source?: string;
    language?: string;
    period_type: string;
    period_length: number;
    start_date: number;
    end_date: number;
}

export type SearchResult = {
    time: number;
    size: number;
    abs_freq: number;
    rel_freq: number;
}

export type SearchResponse = AxiosResponse<SearchResult[]>

export function getSearch(request: SearchRequest): Promise<SearchResponse> {
    request.start_date = toMidnightUTC(request.start_date)
    request.end_date = toMidnightUTC(request.end_date)

    return axios.get("/word_frequency", { params: cleanParams(request) })
}

export function getSVG(request: SearchRequest): Promise<AxiosResponse<string>> {
    return axios.get("/svg", { params: cleanParams(request) })
}
