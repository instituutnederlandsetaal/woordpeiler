import axios, { type AxiosResponse } from "axios"
import { cleanParams } from "@/api/api"

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
    return axios.get("/word_frequency", { params: cleanParams(request) })
}
