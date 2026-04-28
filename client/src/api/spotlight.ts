import axios, { type AxiosResponse } from "axios"
import type { SpotlightConfig } from "@/types/spotlight"
import { config } from "@/main"

export function getSpotlights(): Promise<AxiosResponse<SpotlightConfig>> {
    return axios.get(config.spotlights.url)
}

export function getProxiedSpotlights(): Promise<AxiosResponse<SpotlightConfig>> {
    return axios.get("/spotlights")
}
