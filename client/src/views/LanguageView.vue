<template>
    <HeaderView />
    <main>
        <div class="search">
            <!--Trendsettings-->
            <Accordion value="0" class="p-panel">
                <AccordionPanel value="0">
                    <AccordionHeader>Taalvariëteitinstellingen</AccordionHeader>
                    <AccordionContent class="advancedSearch">
                        <div class="formSplit">
                            <label>Taalvariëteit</label>
                            <SelectButton v-model="trendType" :options="trendTypes" />
                        </div>

                        <div class="formSplit">
                            <label>Uitsluiten</label>
                            <MultiSelect v-model="selectedPosHead" display="chip" :options="posHeadOptions"
                                placeholder="Woordsoort" :loading="posHeadLoading" style="width:70%;" />
                        </div>
                    </AccordionContent>
                </AccordionPanel>
            </Accordion>
            <div class="wordlist">
                <!--Trendlist-->
                <Listbox class="p-panel" v-if="trends.length != 0" multiple metaKeySelection v-model="selectedTrend"
                    :options="trends">
                    <template #option="{ option }">
                        <Badge :value="formatNumber(option.keyness)" severity="secondary" />
                        &nbsp;
                        <span> {{ option.wordform }} </span>
                        &nbsp;
                        <Chip :label="option.poshead" />
                    </template>
                </Listbox>
                <Skeleton v-else />
            </div>
            <SearchOptionsView />
        </div>
        <GraphView />
    </main>
</template>

<script setup lang="ts">
import Skeleton from "primevue/skeleton"
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"

import HeaderView from "@/views/HeaderView.vue"
import GraphView from "@/views/GraphView.vue"
import SearchOptionsView from "@/views/SearchOptionsView.vue"
import Listbox from "primevue/listbox"
import Panel from "primevue/panel"
import SelectButton from "primevue/selectbutton"
import InputNumber from "primevue/inputnumber"
import Chip from "primevue/chip"
import Badge from "primevue/badge"
import MultiSelect from "primevue/multiselect"

import { ref, onMounted, watch } from "vue"
import { useGraphStore, randomColor } from "@/store/GraphStore"
import { apiURL } from "@/ts/api"

const GraphStore = useGraphStore()
const trends = ref([])
const selectedTrend = ref(null)

const timeBucketOptions = [
    { label: "week", value: "week" },
    { label: "maand", value: "month" },
    { label: "jaar", value: "year" },
]
const timeBucketSize = ref(1)
const timeBucketType = ref("year")

const trendTypes = ["keyness", "absolute"]
const trendType = ref()

const selectedPosHead = ref([])
const posHeadOptions = ref([])
const posHeadLoading = ref(true)

watch(selectedTrend, () => {
    GraphStore.dataSeries = []
    for (const trend of Object.values(selectedTrend.value)) {
        GraphStore.dataSeries.push({ wordform: trend.wordform, color: randomColor() })
    }
    GraphStore.search()
})

watch([timeBucketSize, timeBucketType, trendType], () => {
    trends.value = []
    getTrends()
})

function getTrends() {
    let searchParams = {
        period_length: timeBucketSize.value.toString(),
        period_type: timeBucketType.value,
        trend_type: trendType.value,
    }
    searchParams = Object.entries(searchParams).concat(selectedPosHead.value.map((posHead) => ["exclude", posHead]))
    const searchParamsString = new URLSearchParams(searchParams).toString()

    const url = `${apiURL}/trends?${searchParamsString}`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            data.forEach((d) => {
                if (trendType.value == "absolute") d.keyness = d.tc_abs_freq
                trends.value.push(d)
            })
        })
}

function getPosHeadOptions() {
    const url = `${apiURL}/ls/words/poshead`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            posHeadOptions.value = data;
            posHeadLoading.value = false
        })
}

function formatNumber(num: number): number {
    return Math.floor(num * 10) / 10
}

onMounted(() => {
    getTrends()
    getPosHeadOptions()
})
</script>

<style scoped lang="scss">
.wordlist {
    display: flex;
    flex-direction: column;
    gap: 1em;
}
</style>
