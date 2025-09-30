<template>
    <WordInput v-model="wordform" :ngram="config.search.ngram" />
</template>

<script setup lang="ts">
import { config } from "@/main"
import type { SearchItem } from "@/types/search"
import type { SearchTerm } from "@/types/searchTerm"

const item = defineModel<SearchItem>()
const wordform = ref<string | undefined>(item.value?.terms?.map((t: SearchTerm) => t.wordform).join(" "))
watch(wordform, (newVal) => {
    if (newVal) {
        item.value = {
            ...item.value,
            terms: newVal
                .replace(/\s+/g, " ")
                .trim()
                .split(" ")
                .map((w) => ({ wordform: w })),
        }
    } else {
        item.value = { ...item.value, terms: undefined }
    }
})
</script>
