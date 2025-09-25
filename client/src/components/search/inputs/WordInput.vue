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
                    :invalid="invalidInputText(item.wordform)"
                    id="word"
                    placeholder="Woord"
                    v-model.trim="item.wordform"
                    @keyup.enter="search"
                />
            </InputGroup>
        </div>
    </fieldset>
</template>

<script setup lang="ts">
import { useSearchResults } from "@/stores/search/searchResults"
import { type SearchItem, invalidInputText } from "@/types/search"

const { search } = useSearchResults()
const { item } = defineProps<{ item: SearchItem }>()
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
            font-size: 1.1rem;
        }
    }
}
</style>
