<template>
    <fieldset>
        <label for="lemma">Lemma</label>
        <div>
            <InputGroup>
                <InputGroupAddon>
                    <HelpButton>
                        <p>Het lemma is de woordenboekvorm van het woord.</p>
                        <DataTable
                            :value="[
                                { word: 'liep', lemma: 'lopen', pos: 'werkwoord' },
                                { word: 'blauwe', lemma: 'blauw', pos: 'bijvoeglijk naamwoord' },
                                { word: 'huizen', lemma: 'huis', pos: 'zelfstandig naamwoord' },
                            ]"
                            size="small"
                            style="max-width: fit-content"
                        >
                            <Column field="word" header="Woord"></Column>
                            <Column field="lemma" header="Lemma"></Column>
                            <Column field="pos" header="Woordsoort"></Column>
                        </DataTable>
                    </HelpButton>
                </InputGroupAddon>
                <InputText
                    :invalid="invalidText(lemma, ngram)"
                    id="lemma"
                    placeholder="Lemma"
                    v-model.trim="lemma"
                    @keyup.enter="search"
                />
            </InputGroup>
        </div>
    </fieldset>
</template>

<script setup lang="ts">
import { useSearchResults } from "@/stores/search/searchResults"
import { invalidText } from "@/types/search"

const { ngram } = defineProps<{ ngram: number }>()
const { search } = useSearchResults()
const lemma = defineModel<string>({
    set: (value) => {
        if (value) return value
        return undefined
    },
})
</script>
