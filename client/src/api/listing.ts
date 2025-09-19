import axios, { type AxiosResponse } from "axios"

export function getSources(): Promise<AxiosResponse<string[]>> {
    return axios.get(`/sources`)
}

export function getPosses(): Promise<AxiosResponse<string[]>> {
    return axios.get(`/posses`)
}

export function getLanguages(): Promise<AxiosResponse<string[]>> {
    return axios.get(`/languages`)
}
