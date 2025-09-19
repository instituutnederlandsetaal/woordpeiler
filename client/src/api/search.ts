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

export function getSearch(request: SearchRequest): Promise<AxiosResponse<number[][]>> {
    return axios.get("/frequency", { params: cleanParams(request) })
}

export function getSVG(request: SearchRequest): Promise<AxiosResponse<string>> {
    return axios.get("/svg", { params: cleanParams(request) })
}
