import axios from "axios"

export function setAxiosBaseUrl() {
    // On local development, use localhost:8000
    // On production, use host /api
    if (window.location.hostname == "localhost") {
        axios.defaults.baseURL = `${window.location.protocol}//${window.location.hostname}:8000/`
    } else {
        axios.defaults.baseURL = `${window.location.protocol}//${window.location.hostname}/couranten/api/`
    }
}

export function cleanParams(params: Record<string, string>) {
    return Object.fromEntries(Object.entries(params).filter(([_, v]) => v != undefined && v != null && v != ""))
}
