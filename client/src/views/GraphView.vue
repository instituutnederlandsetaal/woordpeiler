<template>
    <div class="graph">
        <div class="p-panel">
            <!-- old -->
            <div v-if="GraphStore.datasets.length === 0" class="emptyGraph">
                <ProgressSpinner />
            </div>
            <D3GraphView v-else :data="data" />
            <!-- new -->
        </div>
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
import D3GraphView from "@/views/D3GraphView.vue"
import { useGraphStore } from "@/store/GraphStore"

const GraphStore = useGraphStore()
const data = computed(() => {
    if (!GraphStore.datasets?.length) {
        return []
        return [
            {
                name: 'kat',
                color: '#ff0000',
                data: [
                    {
                        x: new Date('2020-10-10').getTime(),
                        y: 1,
                    },
                    {
                        x: new Date('2022-10-10').getTime(),
                        y: 7,
                    },
                    {
                        x: new Date().getTime(),
                        y: 2
                    },
                ]
            },
            {
                name: 'hond',
                color: '#00ff00',
                data: [
                    {
                        x: new Date('2020-10-10').getTime(),
                        y: 3,
                    },
                    {
                        x: new Date('2022-10-10').getTime(),
                        y: 6,
                    },
                    {
                        x: new Date().getTime(),
                        y: 4
                    }
                ]
            }
        ]
    }
    const d = GraphStore.datasets
    return d
})

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
        // axis: "xy",
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
