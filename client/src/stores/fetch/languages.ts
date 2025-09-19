import * as API from "@/api/listing"
import { config } from "@/main"
import type { SelectLabel } from "@/types/ui"

export const useLanguages = defineStore("languages", () => {
    const options = ref<SelectLabel[]>()

    function fetch() {
        API.getLanguages().then((res) => {
            options.value = res.data.map(format)
        })
    }

    function format(value: string): SelectLabel { 
        const label = config.language ? `${config.language[value]} (${value})` : value
        return { label, value }
    }

    fetch()

    return { options }
})
