<template>
    <ScrollPanel class="wordlist">
        <Panel toggleable v-for="searchItem in searchItems" :key="searchItem"
            :class="{ 'invalid': invalidSearchItem(searchItem) }">
            <template #header>
                <ColorPicker id="color" v-model="searchItem.color" />
                <div class="panelHeader">
                    <template v-if="displayName(searchItem)"> {{ displayName(searchItem) }} </template>
                    <template v-else></template>
                </div>
            </template>
            <template #icons>
                <Button text severity="secondary" @click="searchItem.visible = !searchItem.visible">
                    <span v-if="searchItem.visible" class="pi pi-eye"></span>
                    <span v-else class="pi pi-eye-slash"></span>
                </Button>
                <Button text severity="secondary" @click="() => searchItems.splice(searchItems.indexOf(searchItem), 1)">
                    <span class="pi pi-trash"></span>
                </Button>
            </template>

            <p class="invalid" v-if="invalidInputText(searchItem.wordform) || invalidInputText(searchItem.lemma)">
                Zoeken op woordgroepen is niet mogelijk.
            </p>

            <div class="formSplit">
                <label for="word">Woord</label><br />
                <InputText :invalid="invalidInputText(searchItem.wordform)" id="word" v-model="searchItem.wordform" />
            </div>

            <template v-if="$internal">
                <div class="formSplit">
                    <label for="lemma">Lemma</label>
                    <InputText :invalid="invalidInputText(searchItem.lemma)" id=" lemma" v-model="searchItem.lemma" />
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
                        placeholder="Krant" />
                </div>
            </template>

            <div class="formSplit">
                <label for="variant">Taalvariëteit</label>
                <Select id="variant" v-model="searchItem.language" :options="languageOptions" showClear
                    optionLabel="label" optionValue="value" placeholder="Taalvariëteit" />
            </div>

        </Panel>
        <Button style="border: 2px dashed #ccc; background: #eee; min-height: 40px" class="newWord" severity="secondary"
            outlined @click="() => searchItems.push({ color: randomColor(), visible: true })">
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

// Lifecycle
onMounted(() =>
    fetchOptions()
)

// onMounted(() => {
//     // read wordform url parameter
//     const urlParams = new URLSearchParams(window.location.search)
//     const wordform = urlParams.get("wordform")
//     if (wordform) {
//         GraphStore.dataSeries.push({ wordform: wordform, color: randomColor() })
//     } else {
//         // retrieve dataseries from cookies
//         if (localStorage.getItem("dataSeries")) {
//             GraphStore.dataSeries = JSON.parse(localStorage.getItem("dataSeries"))
//         } else {
//             // A random new entry when no cookies were stored
//             GraphStore.dataSeries.push({ color: randomColor() })
//         }
//     }
// })

function invalidWord(word?: string): boolean {
    return false
}

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
}

.warning {
    color: red;
    margin-bottom: 0.5rem;
}
</style>