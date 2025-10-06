<template>
    <fieldset>
        <label for="ngram">Aantal woorden</label>
        <Select id="ngram" v-model="ngram" :options optionLabel="label" optionValue="value" placeholder="Lengte" />
    </fieldset>
</template>

<script setup lang="ts">
import { config } from "@/main"
import type { SelectLabel } from "@/types/ui"

const ngram = defineModel<number>()
const options: SelectLabel[] = Array.from({ length: config.search.ngram }, (_, n) => ({
    label: n == 0 ? "1 woord" : `${n + 1} woorden`,
    value: n + 1,
}))
</script>
