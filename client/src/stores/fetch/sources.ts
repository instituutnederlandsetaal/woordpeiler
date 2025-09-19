import * as API from "@/api/listing"
import { config } from "@/main"

export const useSources = defineStore("sources", () => {
    const options = ref<string[]>()

    function fetch() {
        API.getSources().then((res) => {
            options.value = res.data
        })
    }

    if (config.internal) fetch()

    return { options }
})
