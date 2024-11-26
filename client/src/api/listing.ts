import axios, { type AxiosResponse } from "axios"

export function getListing(table: string, column: string): Promise<AxiosResponse<string[]>> {
    return axios.get(`/ls/${table}/${column}`)
}