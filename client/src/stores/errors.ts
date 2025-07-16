import axios from "axios"

export const useErrorsStore = defineStore("Errors", () => {
    // Fields
    const errors = ref<string[]>([])
    // Methods
    function setupErrorHandler() {
        axios.interceptors.response.use(
            (response) => response,
            (error) => {
                // ignore spotlight errors
                if (error.config.url.includes(".json")) {
                    return Promise.reject(error)
                }

                const msg = `${error.config.url.slice(1)}: ${error.message}`
                // If we ever decide to use the detail, uncomment this:
                // const detail = error.response?.data?.detail
                // if (detail) {
                //     msg = `${msg}: ${detail}`
                // }
                errors.value.push(msg)
                return Promise.reject(error)
            },
        )
    }
    // Setup the error handler when the store is created
    setupErrorHandler()
    return { errors }
})
