<template>
    <section>
        <p v-if="!item.terms"><strong> Voer een woord in. </strong></p>
        <p v-if="invalidNgram(item)">
            <strong> Zoek op maximaal {{ config.search.ngram }} woorden. </strong>
        </p>
        <p v-if="invalidStarWildcard(item)">
            <strong> Voer minimaal 4 andere tekens in bij een *-joker. </strong>
        </p>
        <p v-if="invalidQuestionWildcard(item)">
            <strong> Voer minimaal 2 andere tekens in bij een ?-joker. </strong>
        </p>
    </section>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { invalidNgram, invalidStarWildcard, invalidQuestionWildcard, type SearchItem } from "@/types/search"

const { item } = defineProps<{ item: SearchItem }>()
</script>

<style scoped lang="scss">
strong {
    font-weight: normal;
    font-style: italic;
}

section {
    margin-bottom: 0.25rem;
}
</style>
