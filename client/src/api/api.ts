import axios from 'axios'

export function setAxiosBaseUrl() {
    axios.defaults.baseURL = `${window.location.protocol}//${window.location.hostname}:8000/`
}