<template>
    <SimpleNgramInput v-model="ngram" />
    <Accordion v-for="(term, idx) in terms" :key="idx" :value="idx" :class="{ invalid: invalidTerm(term) }">
        <AccordionPanel :value="0">
            <AccordionHeader>
                {{ headerName(idx, term) }}
            </AccordionHeader>
            <AccordionContent>
                <SearchTermValidation :term="term" />
                <AdvancedWordInput v-model="terms[idx]" />
            </AccordionContent>
        </AccordionPanel>
    </Accordion>
</template>

<script setup lang="ts">
import { type SearchItem } from "@/types/search"
import { type SearchTerm, invalidTerm, termToString } from "@/types/searchTerm"

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

function headerName(i: number, term: SearchTerm) {
    const termStr = termToString(term)
    return termStr ? `Woord ${i + 1}: ${termStr}` : `Woord ${i + 1}: lege zoekterm`
}
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
