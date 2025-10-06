import axios, { type AxiosResponse } from "axios"
import type { TrendResult } from "@/types/trends"

export type TrendRequest = {
    trend_type: string
    modifier: number
    start: string
    end: string
    language?: string
    ngram: number
}

export function getTrends(request: TrendRequest): Promise<AxiosResponse<TrendResult[]>> {
    return axios.get("/trends", { params: request })
}
