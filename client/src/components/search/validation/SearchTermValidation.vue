<template>
    <section>
        <p v-if="!term.wordform && !term.lemma"><strong> Voer een woord in. </strong></p>
        <p v-if="invalidNgramText(term.wordform, 1) || invalidNgramText(term.lemma, 1)">
            <strong> Zoek op één woord of pas het aantal woorden aan. </strong>
        </p>
        <p v-if="invalidStarWildcard(dummyItem)">
            <strong> Voer minimaal 4 andere tekens in bij een *-joker. </strong>
        </p>
        <p v-if="invalidQuestionWildcard(dummyItem)">
            <strong> Voer minimaal 2 andere tekens in bij een ?-joker. </strong>
        </p>
    </section>
</template>

<script setup lang="ts">
import { invalidNgramText, invalidStarWildcard, invalidQuestionWildcard, type SearchItem } from "@/types/search"

const dummyItem = computed<SearchItem>(() => ({ terms: [term] }))
const { term } = defineProps<{ term: SearchTerm }>()
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
