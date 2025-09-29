<template>
    <SimpleNgramInput v-model="ngram" />
    <Accordion v-for="(term, idx) in terms" :key="idx" :value="idx" :class="{ invalid: invalidSearchTerm(term) }">
        <AccordionPanel :value="0">
            <AccordionHeader
                >Woord {{ idx + 1 }} {{ termToString(term) ? "&nbsp;" : "" }} {{ termToString(term) }}</AccordionHeader
            >
            <AccordionContent>
                <SearchTermValidation :term="term" />
                <AdvancedWordInput v-model="terms[idx]" />
            </AccordionContent>
        </AccordionPanel>
    </Accordion>
</template>

<script setup lang="ts">
import { type SearchItem, type SearchTerm, invalidSearchTerm } from "@/types/search"
import { termToString } from "@/types/search"

const item = defineModel<SearchItem>()

const terms = ref<SearchTerm[]>(structuredClone(toRaw(item.value?.terms)) ?? [])
const ngram = ref<number>(terms.value.length || 1)
watch(
    ngram,
    (newVal) => {
        // adjust items array length
        while ((terms.value?.length ?? 0) < newVal) {
            terms.value.push({})
        }
        while ((terms.value?.length ?? 0) > newVal) {
            terms.value.pop()
        }
    },
    { immediate: true },
)

watch(
    terms,
    (newVal) => {
        if (newVal.every((t) => t.wordform === undefined && t.lemma === undefined && t.pos === undefined)) {
            item.value = { ...item.value, terms: undefined }
        } else {
            item.value = { ...item.value, terms: newVal }
        }
    },
    { deep: true },
)

// function combine(feature: string) {
//     // combines a feature from all items into a single string, separated by spaces. Null values are replaced by "[]"
//     return items.value.map((i) => i[feature] ?? "[]").join(" ")
// }

// function split(item: SearchItem): SearchTerm[] {
//     // splits a SearchItem into an array of ShallowSearchItems based on spaces in the wordform
//     if (!item.wordform) {
//         return [{ wordform: undefined, pos: undefined, lemma: undefined }]
//     }
//     const wordforms = item.wordform.split(" ")
//     const poses = item.pos ? item.pos.split(" ") : []
//     const lemmas = item.lemma ? item.lemma.split(" ") : []
//     const maxLength = Math.max(wordforms.length, poses.length, lemmas.length)
//     const result: SearchTerm[] = []
//     for (let i = 0; i < maxLength; i++) {
//         result.push({
//             wordform: wordforms[i] === "[]" ? undefined : wordforms[i],
//             pos: poses[i] === "[]" ? undefined : poses[i],
//             lemma: lemmas[i] === "[]" ? undefined : lemmas[i],
//         })
//     }
//     return result
// }
</script>

<style scoped lang="scss">
.p-accordion {
    margin-top: 0.5rem !important;
    .p-accordionheader {
        padding: 0.5rem 0;
    }
    :deep(.p-accordioncontent-content) {
        padding: 0;
    }
}
</style>
