<template>
        <Panel class="search-item" :collapsed toggleable
        :class="{ invalid: invalidSearchItem(item), hidden: !item.visible }"
    >
        <template #header>
            <div>
                <ColorPicker id="color" v-model="item.color" title="Kleur in grafiek" />
                <Button
                    class="visible-btn"
                    text
                    severity="secondary"
                    @click="item.visible = !item.visible"
                >
                    <span v-if="item.visible" class="pi pi-eye" title="Getoond in grafiek"></span>
                    <span v-else class="pi pi-eye-slash" title="Verborgen in grafiek"></span>
                </Button>
            </div>
            <div class="header">
                <template v-if="displayName(item)">
                    {{ displayName(item) }}
                </template>
                <template v-else><i>lege zoekterm</i></template>
            </div>
        </template>

        <template #toggleicon="data">
            <span v-if="data.collapsed" class="pi pi-chevron-down"></span>
            <span v-else class="pi pi-chevron-up"></span>
        </template>

        <template #icons>
            <span v-if="item.loading">
                <span class="pi pi-spin pi-spinner"></span>
            </span>

            <Button
                text
                severity="secondary"
                @click="() => searchItems.splice(searchItems.indexOf(item), 1)"
                title="Verwijderen"
            >
                <span class="pi pi-trash"></span>
            </Button>
        </template>

        <p class="invalid" v-if="invalidInputText(item.lemma) || invalidInputText(item.wordform)">
            Zoek op maximaal {{ config.search.ngram }} woorden.
        </p>

        <p class="invalid" v-if="invalidRegexUsage(item.lemma) || invalidRegexUsage(item.wordform)">
            Voer minimaal 4 andere tekens in dan een *-joker.
        </p>

        <fieldset>
            <label for="word">Woord</label><br />
            <InputText
                :invalid="invalidInputText(item.wordform)"
                id="word"
                v-model.trim="item.wordform"
                @keyup.enter="search"
            />
        </fieldset>

        <fieldset>
            <label for="variant">{{ config.search.filters[0].name }}</label>
            <Select
                id="variant"
                v-model="item.language"
                :options="languageOptions"
                optionLabel="label"
                optionValue="value"
                showClear
                :placeholder="config.search.filters[0].name"
                :loading="!languageOptions"
            />
        </fieldset>
        <Accordion value="-1">
            <AccordionPanel class="advanced">
                <AccordionHeader>Geavanceerd</AccordionHeader>
                <AccordionContent>
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
                                    :invalid="invalidInputText(item.lemma)"
                                    id="lemma"
                                    placeholder="Lemma"
                                    v-model.trim="item.lemma"
                                    @keyup.enter="search"
                                />
                            </InputGroup>
                        </div>
                    </fieldset>
                    <fieldset>
                        <label for="pos">Woordsoort</label>
                        <div>
                            <InputGroup>
                                <InputGroupAddon>
                                    <HelpButton>
                                        <p>
                                            De woordsoorten komen uit de
                                            <a
                                                target="_blank"
                                                href="https://ivdnt.org/wp-content/uploads/2024/11/TDNV2_combi.pdf"
                                                >Tagset Diachroon Nederlands (TDN)</a
                                            >
                                        </p>
                                    </HelpButton>
                                </InputGroupAddon>
                                <Select
                                    :loading="!posOptions"
                                    id="pos"
                                    v-model="item.pos"
                                    :options="posOptions"
                                    optionLabel="label"
                                    optionValue="value"
                                    showClear
                                    placeholder="Woordsoort"
                                />
                            </InputGroup>
                        </div>
                    </fieldset>
                    <template v-if="$internal">
                        <fieldset>
                            <label for="source">{{ config.search.filters[1].name }}</label>
                            <Select
                                id="source"
                                v-model="item.source"
                                :options="sourceOptions"
                                showClear
                                :clearIconProps="{ tabindex: 0 }"
                                :placeholder="config.search.filters[1].name"
                                :loading="!sourceOptions"
                            />
                        </fieldset>
                    </template>
                </AccordionContent>
            </AccordionPanel>
        </Accordion>

        <a v-if="item.wordform && !invalidSearchItem(item)" :href="constructSearchLink(item, searchSettings)" target="_blank">
            {{ searchCorpusText }}
        </a>
    </Panel>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { usePosses } from "@/stores/fetch/posses"
import { useLanguages } from "@/stores/fetch/languages"
import { useSources } from "@/stores/fetch/sources"
import { constructSearchLink } from "@/ts/blacklab/blacklab"
import { useSearchSettings } from "@/stores/search/searchSettings"
import { useSearchResults } from "@/stores/search/searchResults"
import { useSearchItems } from "@/stores/search/searchItems"
import { toYear } from "@/ts/date"
import { displayName, invalidSearchItem, invalidInputText, invalidRegexUsage, type SearchItem } from "@/types/search"

// Props
const { item, collapsed } = defineProps<{ item: SearchItem, collapsed: boolean }>()

// Stores
const { searchItems } = useSearchItems()
const { search } = useSearchResults()
const { searchSettings } = storeToRefs(useSearchSettings())
const { options: posOptions } = storeToRefs(usePosses())
const { options: languageOptions } = storeToRefs(useLanguages())
const { options: sourceOptions } = storeToRefs(useSources())

// Computed
const endYear = computed<string>(() => (config.period.end ? ` ${toYear(config.period.end)}` : "nu"))
const searchCorpusText = computed<string>(() => `Zoeken in ${config.corpus.name} (${toYear(config.period.start)} – ${endYear.value})`)
</script>

<style scoped lang="scss">
.search-item {
    :deep(.p-panel-header) {
        padding-right: 0.5rem !important;
        .p-panel-header-actions > * {
            padding: 0.5rem;
        }
    }
    .header {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
        flex: 1 1 0;
    }
    .p-select,
    .p-inputtext,
    .p-cascadeselect {
        width: 200px;
    }
    .p-inputgroup {
        .p-select,
        .p-inputtext {
            width: 170px;
        }
    }
    .p-inputgroup .p-select {
        align-items: center;
        :deep(span:not(.p-placeholder)) {
            font-size: 0.9rem;
        }
    }
    .p-accordionheader {
        padding: .65rem 0;
    }
    :deep(.p-accordioncontent-content) {
        padding: 0 0 .65rem 0;
    }
    a {
        display: block;
        color: blue;
        // margin: -0.5rem 0;
        font-size: 0.9rem;
    }
    &.hidden {
        filter: brightness(0.9);
    }
    &.invalid {
        border: 2px solid red;
    }
    p.invalid {
        color: red;
        margin-bottom: 0.25rem;
    }
    .visible-btn:focus {
        outline: 1px solid black;
        outline-offset: -3px;
    }
}
</style>