import axios, { type AxiosResponse } from "axios"
import { cleanParams } from "@/api/api"
import { toMidnightUTC } from "@/ts/date"

export type SearchRequest = {
    wordform?: string;
    lemma?: string;
    pos?: string;
    source?: string;
    language?: string;
    interval: string;
    start: string;
    end: string;
}

export type SearchResult = {
    time: number;
    size: number;
    abs_freq: number;
    rel_freq: number;
}

export type SearchResponse = AxiosResponse<SearchResult[]>

export function getSearch(request: SearchRequest): Promise<SearchResponse> {
    return axios.get("/word_frequency", { params: cleanParams(request) })
}

export function getSVG(request: SearchRequest): Promise<AxiosResponse<string>> {
    return axios.get("/svg", { params: cleanParams(request) })
}
