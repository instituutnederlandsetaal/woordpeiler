import axios, { type AxiosResponse } from "axios"
import type { Spotlight } from '@/types/spotlight'

export type SpotlightResponse = AxiosResponse<Spotlight[]>

export function getSpotlights(): Promise<SpotlightResponse> {
    // spotlights uses a different base URL, cross-origin requests are allowed
    // https://ivdnt.org/wp-content/plugins/INT_woordpeiler/woordpeiler.json
    return axios.get("https://ivdnt.org/wp-content/plugins/INT_woordpeiler/woordpeiler.json")
}