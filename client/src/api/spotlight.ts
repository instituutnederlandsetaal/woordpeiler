import axios, { type AxiosResponse } from "axios"
import type { SpotlightConfig } from "@/types/spotlight"

export function getSpotlights(): Promise<AxiosResponse<SpotlightConfig>> {
    return axios.get("https://ivdnt.org/woordpeiler.json")
}


export function getProxiedSpotlights(): Promise<AxiosResponse<SpotlightConfig>> {
    return axios.get("/spotlights")
}
