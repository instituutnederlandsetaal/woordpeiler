<template>
    <fieldset>
        <label for="word">Woord</label><br />
        <div>
            <InputGroup>
                <InputGroupAddon>
                    <HelpButton>
                        <p>U kunt uw zoekopdracht verfijnen met de volgende jokers:</p>
                        <ul>
                            <li>
                                <p><dfn>?</dfn> staat voor exact één willekeurig karakter.</p>
                                <p>
                                    Met <dfn>z?n</dfn> vindt u bijvoorbeeld <em>zon</em>, <em>zin</em> en <em>zen</em>.
                                </p>
                            </li>
                            <li>
                                <p><dfn>*</dfn> staat voor geen, één of meer willekeurige karakters.</p>
                                <p>
                                    Met <dfn>*gebaar</dfn> vindt u bijvoorbeeld <em>gebaar</em>, <em>handgebaar</em> en
                                    <em>vredesgebaar</em>.
                                </p>
                            </li>
                        </ul>
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

<style scoped lang="scss">
ul {
    padding-left: 1rem;
    padding-top: 0.25rem;
    li {
        padding: 0.25rem 0;
        dfn {
            font-style: normal;
            font-weight: bold;
        }
    }
}
</style>
