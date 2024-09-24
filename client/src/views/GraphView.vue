<template>
    <div class="graph">
        <Panel header="graph">
            <template #icons>
                <Button text severity="secondary">
                    <span class="pi pi-download"></span>
                </Button>
            </template>
            <div v-if="GraphStore.datasets.length === 0" class="emptyGraph">
                <ProgressSpinner />
            </div>
            <div style="position: relative" v-else>
                <Line ref=" bar" :data="chartData" :options="chartOptions" />
            </div>
        </Panel>
    </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"

import Panel from "primevue/panel"
import Button from "primevue/button"
import ProgressSpinner from "primevue/progressspinner"
import type { ChartOptions, ChartData } from "chart.js"
import { nl } from "date-fns/locale"
import "chartjs-adapter-date-fns"
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from "chart.js/auto"
import { Bar, Line } from "vue-chartjs"
import { externalTooltipHandler } from "@/ts/tooltip"

import { useGraphStore } from "@/store/GraphStore"

const GraphStore = useGraphStore()

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
// https://stackblitz.com/github/apertureless/vue-chartjs/tree/main/sandboxes/reactive

const bar = ref(null)
const chartData = ref<ChartData<"line">>({ datasets: [] })
const chartOptions = ref<ChartOptions<"line">>({
    locale: "nl",
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    // color: '#0ff',
    // backgroundColor: '#f00',
    // borderColor: '#0F0',
    interaction: {
        intersect: false,
        mode: "index",
    },
    scales: {
        // adapters: {
        //     date: {
        //         locale: nl,
        //     },
        // },
        x: {
            type: "time",

            time: {
                round: "day",
                tooltipFormat: "dd-MM-yyyy",
            },
            title: {
                display: true,
                text: "Date",
                font: {
                    size: 20,
                },
            },
        },
        y: {
            title: {
                display: true,
                text: "Frequency (per million words)",
                padding: 20,
                font: {
                    size: 20,
                },
            },
        },
    },
    elements: {
        point: {
            radius: 6,
            hoverRadius: 7,
            hitRadius: 20,
        },
    },
    plugins: {
        tooltip: {
            interaction: {
                mode: "index",
            },
            enabled: false,
            external: externalTooltipHandler,
        },
        // colors: {
        //     forceOverride: true
        // }
    },
})

watch(
    () => GraphStore.datasets,
    () => {
        chartData.value.datasets = GraphStore.datasets
        let copy = JSON.parse(JSON.stringify(chartData.value))
        chartData.value = copy
    },
    { deep: true }
)
</script>
