import axios from 'axios'

export function setAxiosBaseUrl() {
    axios.defaults.baseURL = `${window.location.protocol}//${window.location.hostname}:8000/`
}

export function cleanParams(params: any) {
    return Object.fromEntries(Object.entries(params).filter(([_, v]) => v != undefined && v != null && v != ""))
}