import axios, { type AxiosResponse } from "axios"
import { cleanParams } from "@/api"
import type { SearchRequest } from "@/api/search"

export type SvgRequest = SearchRequest & { c: string; x: number; y: number; f: string }

export function getSvg(request: SvgRequest): Promise<AxiosResponse<string>> {
    return axios.get("/svg", { params: cleanParams(request) })
}

export function getHuisstijlSvg(request: SvgRequest): Promise<AxiosResponse> {
    return axios.get("/huisstijl-svg", { params: cleanParams(request), responseType: "blob" })
}
