import axios, { type AxiosResponse } from "axios"

export function getSources(): Promise<AxiosResponse<string[]>> {
    return axios.get(`/sources`)
}

export function getPosses(): Promise<AxiosResponse<string[]>> {
    return axios.get(`/posses`)
}

export function getPosheads(): Promise<AxiosResponse<string[]>> {
    return axios.get(`/posheads`)
}