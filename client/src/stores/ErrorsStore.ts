import axios from "axios"
import { defineStore } from "pinia"
import { ref } from "vue"

export const useErrorsStore = defineStore('Errors', () => {
    // Fields
    const errors = ref<string[]>([])
    // Methods
    function setupErrorHandler() {
        axios.interceptors.response.use(
            response => response,
            error => {
                const msg = `${error.config.url.slice(1)}: ${error.message}`
                errors.value.push(msg)
                return Promise.reject(error)
            }
        )
    }
    // export
    return {
        // fields
        errors,
        // methods
        setupErrorHandler
    }
})