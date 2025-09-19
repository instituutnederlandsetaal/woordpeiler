<template>
    <div class="search-items">
        <Panel
            class="search-item"
            :collapsed="defaultCollapse"
            toggleable
            v-for="searchItem in searchItems"
            :key="searchItem"
            :class="{ invalid: invalidSearchItem(searchItem), hidden: !searchItem.visible }"
        >
            <template #header>
                <div>
                    <ColorPicker id="color" v-model="searchItem.color" title="Kleur in grafiek" />
                    <Button
                        class="visible-btn"
                        text
                        severity="secondary"
                        @click="searchItem.visible = !searchItem.visible"
                    >
                        <span v-if="searchItem.visible" class="pi pi-eye" title="Getoond in grafiek"></span>
                        <span v-else class="pi pi-eye-slash" title="Verborgen in grafiek"></span>
                    </Button>
                </div>
                <div class="header">
                    <template v-if="displayName(searchItem)">
                        {{ displayName(searchItem) }}
                    </template>
                    <template v-else><i>lege zoekterm</i></template>
                </div>
            </template>

            <template #toggleicon="data">
                <span v-if="data.collapsed" class="pi pi-chevron-down"></span>
                <span v-else class="pi pi-chevron-up"></span>
            </template>

            <template #icons>
                <span v-if="searchItem.loading">
                    <span class="pi pi-spin pi-spinner"></span>
                </span>

                <Button
                    text
                    severity="secondary"
                    @click="() => searchItems.splice(searchItems.indexOf(searchItem), 1)"
                    title="Verwijderen"
                >
                    <span class="pi pi-trash"></span>
                </Button>
            </template>

            <p class="invalid" v-if="invalidInputText(searchItem.lemma) || invalidInputText(searchItem.wordform)">
                Zoek op maximaal {{ config.search.ngram }} woorden.
            </p>

            <p class="invalid" v-if="invalidRegexUsage(searchItem.lemma) || invalidRegexUsage(searchItem.wordform)">
                Voer minimaal 4 andere tekens in dan een *-joker.
            </p>

            <fieldset>
                <label for="word">Woord</label><br />
                <InputText
                    :invalid="invalidInputText(searchItem.wordform)"
                    id="word"
                    v-model.trim="searchItem.wordform"
                    @keyup.enter="search"
                />
            </fieldset>

            <fieldset>
                <label for="variant">{{ config.search.filters[0].name }}</label>
                <Select
                    id="variant"
                    v-model="searchItem.language"
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
                                        :invalid="invalidInputText(searchItem.lemma)"
                                        id="lemma"
                                        placeholder="Lemma"
                                        v-model.trim="searchItem.lemma"
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
                                    v-model="searchItem.pos"
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
                                    v-model="searchItem.source"
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

            <a
                class="search-corpus"
                :href="constructSearchLink(searchItem, searchSettingsStore.searchSettings)"
                target="_blank"
                v-if="searchItem.wordform && !invalidSearchItem(searchItem)"
            >
                {{ searchCorpusText }}
            </a>
        </Panel>
        <Button
            style=""
            class="add-item-btn"
            severity="secondary"
            title="Zoekterm toevoegen"
            outlined
            @click="() => searchItems.push({ color: randomColor(), visible: true })"
        >
            <span class="pi pi-plus"></span>
        </Button>
    </div>
</template>

<script setup lang="ts">
// Stores
import { useSearchItemsStore } from "@/stores/searchItems"
import { useSearchSettingsStore } from "@/stores/searchSettings"
import { useSearchResultsStore } from "@/stores/searchResults"
// Util
import { displayName, invalidSearchItem, invalidInputText, invalidRegexUsage } from "@/types/search"
import { randomColor } from "@/ts/color"
import { constructSearchLink } from "@/ts/blacklab/blacklab"
import { config } from "@/main"
import { toYear } from "@/ts/date"
import { usePosses } from "@/stores/fetch/posses"
import { useLanguages } from "@/stores/fetch/languages"
import { useSources } from "@/stores/fetch/sources"

// Store
const searchItemsStore = useSearchItemsStore()
const { searchItems } = storeToRefs(searchItemsStore)
const { readURLParams } = searchItemsStore
const { search } = useSearchResultsStore()
const searchSettingsStore = useSearchSettingsStore()
const { loadSearchSettings } = searchSettingsStore
const defaultCollapse = ref<boolean>()

// Select options
const { options: posOptions } = storeToRefs(usePosses())
const { options: languageOptions } = storeToRefs(useLanguages())
const { options: sourceOptions } = storeToRefs(useSources())

// Computed
const searchCorpusText = computed<string>(
    () => `Zoeken in ${config.corpus.name} (${toYear(config.period.start)} – ${endYear.value})`,
)
const endYear = computed<string>(() => {
    return config.period.end ? toYear(config.period.end) : "nu"
})

// Lifecycle
onMounted(() => {
    // read wordform url parameter
    if (new URLSearchParams(window.location.search).size > 0) {
        readURLParams()
        searchSettingsStore.readUrlParams()
        search()
    } else {
        // retrieve dataseries from cookies
        if (localStorage.getItem("searchItems")) {
            searchItems.value = JSON.parse(localStorage.getItem("searchItems"))
            loadSearchSettings()
            search()
        }
    }
    // if there are more than 3 search items
    // default to collapsed panels
    if (searchItems.value.length > 3) {
        defaultCollapse.value = true
    }
})
</script>

<style scoped lang="scss">
.search-items {
    min-height: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding-bottom: 3rem;
    gap: 1rem;
    flex: 5;

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
            .p-select, .p-inputtext {
                width: 170px;
            }
        }
        .search-corpus {
            display: block;
            color: blue;
            margin: -0.5rem 0;
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

    .add-item-btn {
        width: 100%;
        border: 2px dashed #ccc !important;
        background: #eee;
        min-height: 40px;

        &:hover,
        &:active {
            background: #e0e0e0 !important;
        }
        &:focus-visible {
            outline-offset: -1px;
        }
    }
}

@media screen and (max-width: 480px) {
    .search-items {
        gap: 0.5rem;
    }
}
</style>
