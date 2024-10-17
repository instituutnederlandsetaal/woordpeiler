<template>
    <ScrollPanel class="wordlist">
        <Panel toggleable v-for="dataSerie in GraphStore.dataSeries">
            <template #header>
                <ColorPicker id="color" v-model="dataSerie.color" />
                <div class="panelHeader">
                    <template v-if="displayName(dataSerie)"> {{ displayName(dataSerie) }} </template>
                    <template v-else> new word </template>
                </div>
            </template>
            <template #icons>
                <Button text severity="secondary"
                    @click="() => GraphStore.dataSeries.splice(GraphStore.dataSeries.indexOf(dataSerie), 1)">
                    <span class="pi pi-trash"></span>
                </Button>
            </template>

            <div class="formSplit">
                <label for="word">Word</label><br />
                <InputText id="word" v-model="dataSerie.wordform" />
            </div>

            <!-- <Accordion value="1">
                        <AccordionPanel value="0">
                            <AccordionHeader>
                                More options
                            </AccordionHeader>
                            <AccordionContent> -->
            <div class="formSplit">
                <label for="lemma">Lemma</label>
                <InputText id="lemma" v-model="dataSerie.lemma" />
            </div>
            <div class="formSplit">
                <label for="pos">Part of speech</label>
                <CascadeSelect :loading="posLoading" id="pos" v-model="dataSerie.pos" :options="posOptions"
                    optionGroupLabel="label" optionGroupChildren="items" showClear placeholder="Part of speech" />

                <!-- <Select id="pos" v-model="dataSerie.pos" :options="posOptions" optionGroupLabel="label"
                    :loading="posLoading" optionGroupChildren="items" showClear placeholder="Part of speech" /> -->
            </div>
            <div class="formSplit">
                <label for="newspaper">Newspaper</label>
                <Select id="newspaper" :loading="sourceLoading" v-model="dataSerie.newspaper" :options="newspaperOpts"
                    showClear placeholder="Newspaper" />
            </div>

            <div class="formSplit">
                <label for="variant">Variant</label>
                <Select id="variant" v-model="dataSerie.variant" :options="variantOpts" showClear
                    placeholder="Variant" />
            </div>

            <!-- </AccordionContent>
                        </AccordionPanel>
                    </Accordion> -->
        </Panel>
        <Button style="border: 2px dashed #ccc; background: #eee; min-height: 40px" class="newWord" severity="secondary"
            outlined @click="() => GraphStore.dataSeries.push({ color: randomColor() })">
            <span class="pi pi-plus"></span> Add
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

import { useGraphStore, displayName, randomColor } from "@/store/GraphStore"

const GraphStore = useGraphStore()
const posLoading = ref(true)
const posOptions = ref(null)
onMounted(async () => {
    let posHeads = null
    let posses = null
    const posHeadUrl = "http://localhost:8000/ls/words/poshead"
    const posUrl = "http://localhost:8000/ls/words/pos"

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
    posses = posHeads.map((posHead) => {
        return {
            label: posHead,
            items: [posHead].concat(posses.filter((pos) => pos.startsWith(posHead)).map((pos) => {
                return pos
            }))
        }
    })


    posOptions.value = posses
    posLoading.value = false
})

const sourceLoading = ref(true)
const newspaperOpts = ref([])
onMounted(() => {
    const url = "http://localhost:8000/ls/word_frequency/source"
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            newspaperOpts.value = data
            sourceLoading.value = false
        })
})

const variantOpts = ref(["nl", "be"])


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

</script>
