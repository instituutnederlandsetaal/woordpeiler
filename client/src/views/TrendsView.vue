<template>
    <HeaderView />
    <main>
        <div class="search">
            <div class="wordlist">
                <Panel header="Target Period">
                    <div class="timeBucket">
                        <InputNumber v-model="timeBucketSize" inputId="withoutgrouping" :useGrouping="false" fluid />
                        <SelectButton v-model="timeBucketType" :options="timeBucketOptions" />
                    </div>
                    <br />
                    <SelectButton v-model="trendType" :options="trendTypes" />
                </Panel>
                <Listbox
                    v-if="trends.length != 0"
                    multiple
                    metaKeySelection
                    v-model="selectedTrend"
                    :options="trends"
                />
                <Skeleton v-else />
            </div>
            <SearchOptionsView />
        </div>
        <GraphView />
    </main>
</template>

<script setup lang="ts">
import infixRpnEval from "infix-rpn-eval"
import Skeleton from "primevue/skeleton"

import HeaderView from "@/views/HeaderView.vue"
import GraphView from "@/views/GraphView.vue"
import SearchOptionsView from "@/views/SearchOptionsView.vue"
import Listbox from "primevue/listbox"
import Panel from "primevue/panel"
import SelectButton from "primevue/selectbutton"
import DatePicker from "primevue/datepicker"
import InputNumber from "primevue/inputnumber"

import { ref, onMounted, watch } from "vue"
import { useGraphStore, randomColor } from "@/store/GraphStore"

const GraphStore = useGraphStore()
const trends = ref([])
const selectedTrend = ref(null)

const timeBucketOptions = ["day", "week", "month", "year"]
const timeBucketSize = ref(1)
const timeBucketType = ref("year")

const trendTypes = ["keyness", "absolute", "delta"]
const trendType = ref("keyness")

watch(selectedTrend, () => {
    GraphStore.dataSeries = []
    for (const trend of Object.values(selectedTrend.value)) {
        GraphStore.dataSeries.push({ wordform: trend, color: randomColor() })
    }
    GraphStore.search()
})

watch([timeBucketSize, timeBucketType, trendType], () => {
    trends.value = []
    getTrends()
})

function getTrends() {
    const url = `http://localhost:8000/trends?period_length=${timeBucketSize.value}&period_type=${timeBucketType.value}&trend_type=${trendType.value}`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            data.forEach((d) => {
                trends.value.push(d.wordform)
            })
        })
}

onMounted(() => {
    getTrends()
})
</script>

<style scoped lang="scss">
.wordlist {
    display: flex;
    flex-direction: column;
    gap: 1em;
}
</style>
