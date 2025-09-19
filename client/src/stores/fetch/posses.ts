import * as API from "@/api/listing"
import { config } from "@/main"
import type { SelectLabel } from "@/types/ui"

export const usePosses = defineStore("posses", () => {
    const options = ref<SelectLabel[]>()

    function fetch() {
        API.getPosses().then((res) => {
            options.value = res.data
                .filter((p) => !["punct", "__eos__", "res"].includes(p))
                .map(format)
                .sort(sort)
        })
    }

    function format(value: string): SelectLabel {
        const label = config.tagset ? `${config.tagset[value]} (${value})` : value
        return { label, value }
    }

    function sort(a: SelectLabel, b: SelectLabel): number {
        return a.label.localeCompare(b.label)
    }

    fetch()

    return { options }
})
