<template>
    <div class="wordlist">
        <Panel toggleable v-for="searchItem in searchItems" :key="searchItem"
            :class="{ 'invalid': invalidSearchItem(searchItem), 'hidden': !searchItem.visible }">

            <template #header>
                <div>
                    <ColorPicker id="color" v-model="searchItem.color" title="Kleur in grafiek" />
                    <Button text severity="secondary" @click="searchItem.visible = !searchItem.visible">
                        <span v-if="searchItem.visible" class="pi pi-eye" title="Getoond in grafiek"></span>
                        <span v-else class="pi pi-eye-slash" title="Verborgen in grafiek"></span>
                    </Button>
                </div>
                <div class="panelHeader">
                    <template v-if="displayName(searchItem)"> {{ displayName(searchItem) }} </template>
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

                <Button text severity="secondary" @click="() => searchItems.splice(searchItems.indexOf(searchItem), 1)"
                    title="Verwijderen">
                    <span class="pi pi-trash"></span>
                </Button>
            </template>

            <p class="invalid" v-if="invalidInputText(searchItem.lemma) || invalidInputText(searchItem.wordform)">
                Zoeken op woordgroepen is niet mogelijk.
            </p>
            <p class="invalid" v-if="searchItem.language && searchItem.source">Kies óf een <b>krant</b> óf een
                <b>taalvariëteit</b>.
            </p>

            <div class="formSplit">
                <label for="word">Woord</label><br />
                <InputText :invalid="invalidInputText(searchItem.wordform)" id="word" v-model.trim="searchItem.wordform"
                    @keyup.enter="search" />
            </div>

            <template v-if="$internal">
                <div class="formSplit">
                    <label for="lemma">Lemma</label>
                    <InputText :invalid="invalidInputText(searchItem.lemma)" id="lemma" v-model.trim="searchItem.lemma"
                        @keyup.enter="search" />
                </div>
                <div class="formSplit">
                    <label for="pos">Woordsoort</label>
                    <CascadeSelect :loading="!Object.entries(posOptions).length" id="pos" v-model="searchItem.pos"
                        :options="posOptions" optionGroupLabel="label" optionGroupChildren="items" showClear
                        placeholder="Woordsoort" />


                </div>
                <div class="formSplit">
                    <label for="source">Krant</label>
                    <Select id="source" v-model="searchItem.source" :options="sourceOptions" showClear
                        placeholder="Krant" :loading="!sourceOptions.length"
                        :invalid="searchItem.language && searchItem.source" />
                </div>
            </template>

            <div class="formSplit">
                <label for="variant">Taalvariëteit</label>
                <Select id="variant" v-model="searchItem.language" :options="languageOptions" showClear
                    optionLabel="label" optionValue="value" placeholder="Taalvariëteit"
                    :invalid="searchItem.language && searchItem.source" />
            </div>

            <a class="searchCHN" :href="constructSearchLink(searchItem, searchSettingsStore.searchSettings)"
                target="_blank" v-if="searchItem.wordform && !invalidSearchItem(searchItem)">
                Zoeken in CHN (2000 &ndash; nu)
            </a>

        </Panel>
        <Button style="border: 2px dashed #ccc; background: #eee; min-height: 40px" class="newWord" severity="secondary"
            title="Zoekterm toevoegen" outlined
            @click="() => searchItems.push({ color: randomColor(), visible: true })">
            <span class="pi pi-plus"></span>
        </Button>
    </div>
</template>

<script setup lang="ts">
// Libraries
import { onMounted } from "vue"
import { storeToRefs } from 'pinia'
// Stores
import { useSearchItemsStore } from "@/stores/SearchItemsStore"
import { useSearchSettingsStore } from "@/stores/SearchSettingsStore"
import { useSearchResultsStore } from "@/stores/SearchResultsStore"
// Components
import InputText from "primevue/inputtext"
import ColorPicker from "primevue/colorpicker"
import Panel from "primevue/panel"
import Button from "primevue/button"
import Select from "primevue/select"
import CascadeSelect from 'primevue/cascadeselect'
// Util
import { displayName, invalidSearchItem, invalidInputText } from "@/types/Search"
import { randomColor } from "@/ts/color"
import { constructSearchLink } from "@/ts/blacklab/blacklab"

// Store
const searchItemsStore = useSearchItemsStore()
const { searchItems, posOptions, sourceOptions, languageOptions } = storeToRefs(searchItemsStore)
const { fetchOptions, readURLParams } = searchItemsStore
const { search } = useSearchResultsStore()
const searchSettingsStore = useSearchSettingsStore()
const { loadSearchSettings } = searchSettingsStore

// Lifecycle
onMounted(() =>
    fetchOptions()
)

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

        &:hover,
        &:active {
            background: #e0e0e0 !important;
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

.hidden {
    filter: brightness(0.9);
}

:deep(.p-panel-header-actions)>* {
    display: inline-flex;
    font-size: 16px;
    padding: 0.5rem;
    margin: 0;
}

:deep(.p-panel-header) {
    padding-right: 0.5rem !important;
}
</style>