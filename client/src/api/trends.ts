import axios, { type AxiosResponse } from "axios"
import type { TrendResult } from "@/types/trends"

export type TrendResponse = AxiosResponse<TrendResult[]>

export type TrendRequest = {
    trend_type: string
    modifier: number
    start: string
    end: string
    enriched: boolean
    language?: string
    ascending: boolean
    ngram: number
}

export function getTrends(request: TrendRequest): Promise<TrendResponse> {
    return axios.get("/trends", { params: request })
}
