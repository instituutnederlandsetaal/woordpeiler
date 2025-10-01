<template>
    <fieldset>
        <label for="word">Woord</label><br />
        <div>
            <InputGroup>
                <InputGroupAddon>
                    <HelpButton>
                        <WildcardHelp />
                    </HelpButton>
                </InputGroupAddon>

                <InputText
                    :invalid="invalidText(wordform, ngram)"
                    id="word"
                    placeholder="Woord"
                    v-model="wordform"
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
const wordform = defineModel<string>({
    set: (value) => {
        if (value) return value
        return undefined
    },
})
</script>
