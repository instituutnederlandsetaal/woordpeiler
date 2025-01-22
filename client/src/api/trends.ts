import type { TrendResult } from "@/types/trends"
import axios, { type AxiosResponse } from "axios"
import { toMidnightUTC } from "@/ts/date"

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
    request.start_date = toMidnightUTC(request.start_date)
    request.end_date = toMidnightUTC(request.end_date)
    return axios.get("/trends", { params: request })
}
