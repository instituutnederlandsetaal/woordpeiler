<template>
    <div class="wordlist">
        <Panel
            :collapsed="defaultCollapse"
            toggleable
            v-for="searchItem in searchItems"
            :key="searchItem"
            :class="{ invalid: invalidSearchItem(searchItem), hidden: !searchItem.visible }"
        >
            <template #header>
                <div>
                    <ColorPicker id="color" v-model="searchItem.color" title="Kleur in grafiek" />
                    <Button class="visibleBtn" text severity="secondary" @click="searchItem.visible = !searchItem.visible">
                        <span v-if="searchItem.visible" class="pi pi-eye" title="Getoond in grafiek"></span>
                        <span v-else class="pi pi-eye-slash" title="Verborgen in grafiek"></span>
                    </Button>
                </div>
                <div class="panelHeader">
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
                Zoek op een woordgroep van maximaal {{ config.searchItems.ngram }} woorden.
            </p>

            <p class="invalid" v-if="invalidRegexUsage(searchItem.lemma) || invalidRegexUsage(searchItem.wordform)">
                Voer minimaal 4 andere tekens in dan een *-joker.
            </p>

            <div class="formSplit">
                <label for="word">Woord</label><br />
                <InputText
                    :invalid="invalidInputText(searchItem.wordform)"
                    id="word"
                    v-model.trim="searchItem.wordform"
                    @keyup.enter="search"
                />
            </div>

            <div class="formSplit">
                <label for="variant">{{ config.searchItems.filters[0].name }}</label>
                <Select
                    id="variant"
                    v-model="searchItem.language"
                    :options="languageOptions"
                    showClear
                    :placeholder="config.searchItems.filters[0].name"
                    :loading="!languageOptions.length"
                />
            </div>
            <Accordion value="-1">
                <AccordionPanel class="advanced">
                    <AccordionHeader>Geavanceerd</AccordionHeader>
                    <AccordionContent>
                        <div class="formSplit">
                            <label for="lemma">Lemma
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
                            </label>
                            <InputText
                                :invalid="invalidInputText(searchItem.lemma)"
                                id="lemma"
                                placeholder="Lemma"
                                v-model.trim="searchItem.lemma"
                                @keyup.enter="search"
                            />
                        </div>
                        <div class="formSplit">
                            <label for="pos">Woordsoort</label>
                            <CascadeSelect
                                :loading="!Object.entries(posOptions).length"
                                id="pos"
                                v-model="searchItem.pos"
                                :options="posOptions"
                                optionGroupLabel="label"
                                optionGroupChildren="items"
                                showClear
                                placeholder="Woordsoort"
                            />
                        </div>
                        <template v-if="$internal">
                            <div class="formSplit">
                                <label for="source">{{ config.searchItems.filters[1].name }}</label>
                                <Select
                                    id="source"
                                    v-model="searchItem.source"
                                    :options="sourceOptions"
                                    showClear
                                    :clearIconProps="{tabindex: 0}"
                                    :placeholder="config.searchItems.filters[1].name"
                                    :loading="!sourceOptions.length"
                                />
                            </div>
                        </template>
                    </AccordionContent>
                </AccordionPanel>
            </Accordion>

            <a
                class="searchCHN"
                :href="constructSearchLink(searchItem, searchSettingsStore.searchSettings)"
                target="_blank"
                v-if="searchItem.wordform && !invalidSearchItem(searchItem)"
            >
                {{ searchCorpusText }}
            </a>
        </Panel>
        <Button
            style=""
            class="newWord"
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

// Store
const searchItemsStore = useSearchItemsStore()
const { searchItems, posOptions, sourceOptions, languageOptions } = storeToRefs(searchItemsStore)
const { fetchOptions, readURLParams } = searchItemsStore
const { search } = useSearchResultsStore()
const searchSettingsStore = useSearchSettingsStore()
const { loadSearchSettings } = searchSettingsStore
const defaultCollapse = ref<boolean>()

// Computed
const searchCorpusText = computed<string>(
    () => `Zoeken in ${config.corpus.name} (${toYear(config.period.start)} – ${endYear.value})`,
)
const endYear = computed<string>(() => {
    return config.period.end ? toYear(config.period.end) : "nu"
})

// Lifecycle
onMounted(() => fetchOptions())

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
.wordlist {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding-bottom: 3rem;
    gap: 1rem;

    .newWord {
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

    .searchCHN {
        display: block;
        color: blue;
        margin-top: 0.3em;
        margin-bottom: -0.5rem;
        font-size: 0.9rem;
    }
}

.wordlist {
    .p-select,
    .p-inputtext,
    .p-cascadeselect {
        width: 200px;
    }
}

.hidden {
    filter: brightness(0.9);
}

.visibleBtn:focus {
    outline: 1px solid black;
    outline-offset: -3px;
}

:deep(.p-panel-header-actions) > * {
    display: inline-flex;
    font-size: 16px;
    padding: 0.5rem;
    margin: 0;
}

:deep(.p-panel-header) {
    padding-right: 0.5rem !important;
}
</style>
