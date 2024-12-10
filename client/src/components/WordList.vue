<template>
    <ScrollPanel class="wordlist">
        <Panel toggleable v-for="searchItem in searchItems" :key="searchItem"
            :class="{ 'invalid': invalidSearchItem(searchItem) }">

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

            <template #icons>
                <span v-if="searchItem.loading">
                    <span class="pi pi-spin pi-spinner"></span>
                </span>

                <Button text severity="secondary" @click="() => searchItems.splice(searchItems.indexOf(searchItem), 1)"
                    title="Verwijderen">
                    <span class="pi pi-trash"></span>
                </Button>
            </template>

            <p class="invalid" v-if="invalidInputText(searchItem.lemma)">
                Zoeken op woordgroepen is niet mogelijk.
            </p>

            <div class="formSplit">
                <label for="word">Woord</label><br />
                <InputText id="word" v-model="searchItem.wordform" @keyup.enter="search" />
            </div>

            <template v-if="$internal">
                <div class="formSplit">
                    <label for="lemma">Lemma</label>
                    <InputText :invalid="invalidInputText(searchItem.lemma)" id=" lemma" v-model="searchItem.lemma"
                        @keyup.enter="search" />
                </div>
                <div class="formSplit">
                    <label for="pos">Woordsoort</label>
                    <CascadeSelect :loading="!Object.entries(posOptions).length" id="pos" v-model="searchItem.pos"
                        :options="posOptions" optionGroupLabel="label" optionGroupChildren="items" showClear
                        placeholder="Woordsoort" />

                </div>
                <div class="formSplit">
                    <label for="newspaper">Krant</label>
                    <Select id="newspaper" v-model="searchItem.newspaper" :options="sourceOptions" showClear
                        placeholder="Krant" :loading="!sourceOptions.length" />
                </div>
            </template>

            <div class="formSplit">
                <label for="variant">Taalvariëteit</label>
                <Select id="variant" v-model="searchItem.language" :options="languageOptions" showClear
                    optionLabel="label" optionValue="value" placeholder="Taalvariëteit" />
            </div>

        </Panel>
        <Button style="border: 2px dashed #ccc; background: #eee; min-height: 40px" class="newWord" severity="secondary"
            title="Zoekterm toevoegen" outlined
            @click="() => searchItems.push({ color: randomColor(), visible: true })">
            <span class="pi pi-plus"></span>
        </Button>
    </ScrollPanel>
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
import ScrollPanel from "primevue/scrollpanel"
import Select from "primevue/select"
import CascadeSelect from 'primevue/cascadeselect'
// Util
import { displayName, invalidSearchItem, invalidInputText } from "@/types/Search"
import { randomColor } from "@/ts/color"

// Store
const searchItemsStore = useSearchItemsStore()
const { searchItems, posOptions, sourceOptions, languageOptions } = storeToRefs(searchItemsStore)
const { fetchOptions } = searchItemsStore
const { search } = useSearchResultsStore()
const { loadSearchSettings } = useSearchSettingsStore()

// Lifecycle
onMounted(() =>
    fetchOptions()
)

onMounted(() => {
    // read wordform url parameter
    const urlParams = new URLSearchParams(window.location.search)
    const wordform = urlParams.get("wordform")
    if (wordform) {
        searchItems.value.push({ wordform: wordform, color: randomColor() })
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
    overflow: auto;

    :deep(.p-scrollpanel-content) {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .newWord {
        width: 100%;

        &:hover,
        &:active {
            background: #e0e0e0 !important;
        }
    }
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