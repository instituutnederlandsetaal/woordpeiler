<template>
    <ScrollPanel class="wordlist">
        <Panel toggleable v-for="dataSerie in GraphStore.dataSeries">
            <template #header>
                <ColorPicker id="color" v-model="dataSerie.color" />
                <div class="panelHeader">
                    <template v-if="displayName(dataSerie)"> {{ displayName(dataSerie) }} </template>
                    <template v-else></template>
                </div>
            </template>
            <template #icons>
                <Button text severity="secondary"
                    @click="() => GraphStore.dataSeries.splice(GraphStore.dataSeries.indexOf(dataSerie), 1)">
                    <span class="pi pi-trash"></span>
                </Button>
            </template>

            <p class="warning" v-if="invalidWord(dataSerie.wordform) || invalidWord(dataSerie.lemma)">Zoeken op meerdere
                woorden is
                niet mogelijk.</p>

            <div class="formSplit">
                <label for="word">Woord</label><br />
                <InputText :invalid="invalidWord(dataSerie.wordform)" id="word" v-model="dataSerie.wordform" />
            </div>

            <!-- <Accordion value="1">
                        <AccordionPanel value="0">
                            <AccordionHeader>
                                More options
                            </AccordionHeader>
                            <AccordionContent> -->
            <div class="formSplit">
                <label for="lemma">Lemma</label>
                <InputText :invalid="invalidWord(dataSerie.lemma)" id=" lemma" v-model="dataSerie.lemma" />
            </div>
            <div class="formSplit">
                <label for="pos">Woordsoort</label>
                <CascadeSelect :loading="posLoading" id="pos" v-model="dataSerie.pos" :options="posOptions"
                    optionGroupLabel="label" optionGroupChildren="items" showClear placeholder="Woordsoort" />

                <!-- <Select id="pos" v-model="dataSerie.pos" :options="posOptions" optionGroupLabel="label"
                    :loading="posLoading" optionGroupChildren="items" showClear placeholder="Part of speech" /> -->
            </div>
            <div class="formSplit">
                <label for="newspaper">Krant</label>
                <Select id="newspaper" :loading="sourceLoading" v-model="dataSerie.newspaper" :options="newspaperOpts"
                    showClear placeholder="Krant" />
            </div>

            <div class="formSplit">
                <label for="variant">Taalvariëteit</label>
                <Select id="variant" v-model="dataSerie.language" :options="variantOpts" showClear optionLabel="label"
                    optionValue="value" placeholder="Taalvariëteit" />
            </div>

            <!-- </AccordionContent>
                        </AccordionPanel>
                    </Accordion> -->
        </Panel>
        <Button style="border: 2px dashed #ccc; background: #eee; min-height: 40px" class="newWord" severity="secondary"
            outlined @click="() => GraphStore.dataSeries.push({ color: randomColor() })">
            <span class="pi pi-plus"></span>
        </Button>
    </ScrollPanel>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext"
import ColorPicker from "primevue/colorpicker"
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"
import FloatLabel from "primevue/floatlabel"
import Panel from "primevue/panel"
import Card from "primevue/card"
import Button from "primevue/button"
import ProgressSpinner from "primevue/progressspinner"
import ScrollPanel from "primevue/scrollpanel"
import Skeleton from "primevue/skeleton"
import Select from "primevue/select"
import SelectButton from "primevue/selectbutton"
import DatePicker from "primevue/datepicker"
import InputNumber from "primevue/inputnumber"
import CascadeSelect from 'primevue/cascadeselect';

import { computed, onMounted, ref, watch } from "vue"

import { useGraphStore, displayName } from "@/store/GraphStore"
import { randomColor } from "@/ts/color"

import { apiURL } from "@/ts/api"

const GraphStore = useGraphStore()
const posLoading = ref(true)
const posOptions = ref(null)
onMounted(async () => {
    let posHeads = null
    let posses = null
    const posHeadUrl = `${apiURL}/ls/words/poshead`
    const posUrl = `${apiURL}/ls/words/pos`

    await fetch(posHeadUrl)
        .then((response) => response.json())
        .then((data) => {
            posHeads = data
        })
    await fetch(posUrl)
        .then((response) => response.json())
        .then((data) => {
            posses = data
        })

    // posses is now in the form [NOU(num=sg), NOU(num=pl), AA, ...]
    // We want to transform this into [{label: "NOU", items: [{label: "NOU(num=sg)", value: "NOU(num=sg)"}]}, {label: "AA", items: ...]}, ...]
    posses = posHeads.filter(posHead => !["punct", "__eos__"].includes(posHead)).map((posHead) => {
        return {
            label: posHead,
            items: [posHead].concat(posses.filter((pos) => pos.startsWith(posHead) && pos.includes("(") && !pos.includes("()")).map((pos) => {
                return pos
            }))
        }

    })
    // Remove punct and __eos__

    posOptions.value = posses
    posLoading.value = false
})

const sourceLoading = ref(true)
const newspaperOpts = ref([])
onMounted(() => {
    const url = `${apiURL}/ls/sources/source`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            newspaperOpts.value = data
            sourceLoading.value = false
        })
})

const variantOpts = ref([
    { label: "Antilliaans-Nederlands", value: "AN" },
    { label: "Belgisch-Nederlands", value: "BN" },
    { label: "Nederlands-Nederlands", value: "NN" },
    { label: "Surinaams-Nederlands", value: "SN" },
])


onMounted(() => {
    // read wordform url parameter
    const urlParams = new URLSearchParams(window.location.search)
    const wordform = urlParams.get("wordform")
    if (wordform) {
        GraphStore.dataSeries.push({ wordform: wordform, color: randomColor() })
    } else {
        // retrieve dataseries from cookies
        if (localStorage.getItem("dataSeries")) {
            GraphStore.dataSeries = JSON.parse(localStorage.getItem("dataSeries"))
        } else {
            // A random new entry when no cookies were stored
            GraphStore.dataSeries.push({ color: randomColor() })
        }
    }
    GraphStore.search()
})

function invalidWord(word: string): boolean {
    return word.trim().includes(" ")
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