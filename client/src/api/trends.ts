import type { TrendSettings } from "@/types/trends"
import axios, { type AxiosResponse } from "axios"

export interface TrendItem {
    wordform: string
    poshead: string
    keyness: number
}

export type TrendResponse = AxiosResponse<TrendItem[]>

export function getTrends(request: TrendSettings): Promise<TrendResponse> {
    return axios.get("/trends", { params: request })
}
