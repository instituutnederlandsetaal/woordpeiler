<template>
    <HeaderView />
    <main>
        <div class="search">
            <!--Trendsettings-->
            <Accordion :value="tabOpen" class="p-panel" ref="trendAccordion">
                <AccordionPanel value="0">
                    <AccordionHeader>Trendinstellingen</AccordionHeader>
                    <AccordionContent class="advancedSearch">
                        <div class="formSplit">
                            <label>Afgelopen</label>
                            <InputNumber class="modifierInput" v-model="timeBucketSize" inputId="withoutgrouping"
                                :useGrouping="false" />
                            <SelectButton v-model="timeBucketType" :options="timeBucketOptions" optionValue="value"
                                optionLabel="label" />
                        </div>

                        <div class="formSplit">
                            <label>Trendsoort</label>
                            <SelectButton v-model="trendType" :options="trendTypes" optionValue="value"
                                optionLabel="label" />
                        </div>

                        <div class="formSplit">
                            <label>{{ modifierLabel }}</label>
                            <InputNumber class="modifierInput" v-model="modifier" inputId="withoutgrouping"
                                :useGrouping="false" />
                        </div>



                        <Button class="search-btn" label="Berekenen" @click="getTrends" />
                    </AccordionContent>
                </AccordionPanel>
            </Accordion>

            <Panel v-if="filteredTrends.length != 0" header="Trendresultaten" class="trendlist">
                <div class="formSplit">
                    <label>Uitsluiten</label>
                    <MultiSelect v-model="selectedPosHead" display="chip" :options="posHeadOptions"
                        placeholder="Woordsoort" :loading="posHeadLoading" style="width:70%;" />
                </div>


                <Listbox class="p-panel" multiple metaKeySelection v-model="selectedTrend" filter
                    :options="filteredTrends" optionLabel="wordform">
                    <template #option="{ option }">
                        <Badge :value="formatNumber(option.keyness)" severity="secondary" />
                        &nbsp;
                        <span> {{ option.wordform }} </span>
                        &nbsp;
                        <Chip :label="option.poshead" />
                    </template>
                </Listbox>
            </Panel>

            <Skeleton class="trendlist" v-else-if="trendsLoading" />


            <SearchOptionsView />
        </div>
        <GraphView />
    </main>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue"
import { useGraphStore } from "@/store/GraphStore"
import { randomColor } from "@/ts/color"
import { apiURL } from "@/ts/api"
// Components
import Skeleton from "primevue/skeleton"
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"
import Button from "primevue/button"
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

// stores
const GraphStore = useGraphStore()

// fields
/** trends multiselect */
const trends = ref([])
const trendsLoading = ref(false)
const selectedTrend = ref(null)
/** trends accordion */
const trendAccordion = ref()
const tabOpen = ref("0")
/** timebucket */
const timeBucketOptions = [
    { label: "week", value: "week" },
    { label: "maand", value: "month" },
    { label: "jaar", value: "year" },
]
const timeBucketSize = ref(1)
const timeBucketType = ref("year")
/** trend types */
const trendTypes = [
    { label: "keyness", value: "keyness" },
    { label: "absolute frequentie", value: "absolute" }
]
const trendType = ref("keyness")
/** poshead exclusion */
const selectedPosHead = ref(["nou-p", "res", "num"])
const posHeadOptions = ref([])
const posHeadLoading = ref(true)
/** modifier */
const modifier = ref(1)
/** What does the modifier mean */
const modifierLabels = {
    keyness: "Smoothingparameter",
    absolute: "Maximumfrequentie in referentiecorpus",
}
const modifierLabel = computed(() => modifierLabels[trendType.value])



// computed
const filteredTrends = computed(() => {
    return trends.value.filter((i) => !selectedPosHead.value.includes(i.poshead))
})

// Methods
/** search trends */
function getTrends() {
    trends.value = []
    tabOpen.value = parseInt(tabOpen.value) + 1;
    let searchParams = {
        period_length: timeBucketSize.value.toString(),
        period_type: timeBucketType.value,
        trend_type: trendType.value,
        modifier: modifier.value.toString(),
    }
    searchParams = Object.entries(searchParams).concat(selectedPosHead.value.map((posHead) => ["exclude", posHead]))
    const searchParamsString = new URLSearchParams(searchParams).toString()

    const url = `${apiURL}/trends?${searchParamsString}`
    trendsLoading.value = true
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            data.forEach((d) => {
                // if (trendType.value == "absolute") d.keyness = d.tc_abs_freq
                trends.value.push(d)
            })
        })
        .finally(() => {
            trendsLoading.value = false
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

// Lifecycle
onMounted(() => {
    getPosHeadOptions()
})

watch(selectedTrend, () => {
    GraphStore.dataSeries = []
    for (const trend of Object.values(selectedTrend.value)) {
        GraphStore.dataSeries.push({ wordform: trend.wordform, pos: trend.pos, color: randomColor() })
    }
    GraphStore.search()
})
</script>

<style scoped lang="scss">
.modifierInput {
    flex-basis: 60px;

    :deep(input) {
        width: 100%;
    }
}

:deep(.trendlist) {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    .p-panel-content-container {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;

        .p-panel-content {
            flex: 1;
            min-height: 0;
            display: flex;
            flex-direction: column;

            .p-listbox {
                flex: 1;
                min-height: 0;
                display: flex;
                flex-direction: column;
                margin-top: 0.5rem;

                .p-listbox-list-container {
                    flex: 1;
                    max-height: none !important;
                    min-height: 0 !important;
                }
            }
        }
    }
}
</style>