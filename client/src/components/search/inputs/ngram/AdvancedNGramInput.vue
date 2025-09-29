<template>
    <fieldset>
        <label for="ngram">N-gram</label>
        <Select id="ngram" v-model="ngram" :options optionLabel="label" optionValue="value" placeholder="N-gram" />
    </fieldset>
</template>

<script setup lang="ts">
import { config } from "@/main"
import type { SelectLabel } from "@/types/ui"

const ngram = defineModel<number>()
const options: SelectLabel[] = generateNGramOptions()
// Methods
function generateNGramOptions(): SelectLabel[] {
    const options: SelectLabel[] = []
    for (let n = 1; n <= config.search.ngram; n++) {
        options.push({ label: `${n}-gram`, value: n })
    }
    return options
}
</script>
