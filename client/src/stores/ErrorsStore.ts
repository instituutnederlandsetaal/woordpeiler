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
                errors.value.push(error.message)
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