<template>
    <WordInput v-model="item.wordform" :ngram="1" />
    <LemmaInput v-model="item.lemma" :ngram="1" />
    <PosInput v-model="item.pos" />
</template>

<script setup lang="ts">
import type { SearchTerm } from "@/types/searchTerm"

const item = defineModel<SearchTerm>()
</script>
