import axios, { type AxiosResponse } from "axios"
import { cleanParams } from "@/api"

export type SearchRequest = {
    w?: string
    l?: string
    p?: string
    s?: string
    v?: string
    i: string
    start: string
    end: string
}

export type SearchResult = { time: number; size: number; abs_freq: number; rel_freq: number }

export type SearchResponse = AxiosResponse<SearchResult[]>

export function getSearch(request: SearchRequest): Promise<SearchResponse> {
    return axios.get("/frequency", { params: cleanParams(request) })
}

export function getSVG(request: SearchRequest): Promise<AxiosResponse<string>> {
    return axios.get("/svg", { params: cleanParams(request) })
}
