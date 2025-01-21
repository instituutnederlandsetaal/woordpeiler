import type { TrendResult } from "@/types/trends"
import axios, { type AxiosResponse } from "axios"

export type TrendResponse = AxiosResponse<TrendResult[]>

export type TrendRequest = {
    trend_type: string;
    modifier: number;
    start_date: number;
    end_date: number;
    enriched: boolean;
    language?: string;
    ascending: boolean;
}

export function getTrends(request: TrendRequest): Promise<TrendResponse> {
    return axios.get("/trends", { params: request })
}
