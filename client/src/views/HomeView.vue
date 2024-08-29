<template>
    <div class="search">
        <p>wordform(s) (comma-separated):</p>
        <form v-on:submit.prevent>
            <input type="text" v-model="wordform" placeholder="wordform" />
            <input type="submit" value="search" @click="search()" />
        </form>
        <p>options:</p>
        <label>
            <input type="checkbox" v-model="isAbsolute" />
            absolute
        </label>
        <label>
            <input type="checkbox" v-model="shouldZeroPad" />
            zero pad
        </label>
        <input type="number" v-model="periodLength" />
        <select v-model="periodType">
            <option v-for="option in periods" :value="option.value" :key="option.value">
                {{ option.text }}
            </option>
        </select>
    </div>
    <div class="container">
        <Line ref="bar" :data="chartData" :options="chartOptions" :styles />
    </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ChartOptions, ChartData } from 'chart.js';
import { nl } from 'date-fns/locale';
import 'chartjs-adapter-date-fns';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js/auto'
import { Bar, Line } from 'vue-chartjs'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
// https://stackblitz.com/github/apertureless/vue-chartjs/tree/main/sandboxes/reactive

const isAbsolute = ref(true)
const shouldZeroPad = ref(false)
const wordform = ref('')
const datasets = ref([])
const periods = [{ text: 'day(s)', value: 'day' }, { text: 'week(s)', value: 'week' }, { text: 'month(s)', value: 'month' }, { text: 'year(s)', value: 'year' }]
const periodType = ref('day')
const periodLength = ref(1)

const bar = ref(null)
const chartData = ref<ChartData<'line'>>({
    datasets: [
        {
            label: 'lopen',
            data: [{ x: 1619500411 * 1000, y: 40 }, { x: 1719500411 * 1000, y: 20 }],
        },
        {
            label: 'zwevne',
            data: [{ x: 1619500411 * 1000, y: 30 }, { x: 1719500411 * 1000, y: 60 }],
        },
    ],
})
const chartOptions = ref<ChartOptions<'line'>>({
    locale: 'nl',
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    // color: '#0ff',
    // backgroundColor: '#f00',
    // borderColor: '#0F0',
    interaction: {
        intersect: false,
        mode: 'index',
    },
    scales: {
        // adapters: {
        //     date: {
        //         locale: nl,
        //     },
        // },
        x: {
            type: 'time',

            time: {
                round: 'day',
                tooltipFormat: 'dd-MM-yyyy',
            },
            title: {
                text: 'Date',
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
        colors: {
            forceOverride: true
        }
    }
})
const styles = ref({
    height: '300px',
    width: '100%',
    position: 'relative',
})

function getFrequency(wordform) {
    // api call
    const url = `http://localhost:8000/word_frequency?wordform=${wordform}&zero_pad=${shouldZeroPad.value}&absolute=${isAbsolute.value}&period_length=${periodLength.value}&period_type=${periodType.value}`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            // data is in the form [{time: 1619500411, value: 40}, {time: 1719500411, value: 20}]
            const dataset = {
                label: wordform,
                data: data.map((d) => {
                    return { x: d.time * 1000, y: d.frequency }
                }),
            }
            datasets.value.push(dataset)
        })
}

function update(datasets) {
    chartData.value.datasets = datasets
    let copy = JSON.parse(JSON.stringify(chartData.value))
    chartData.value = copy
    // chartData.value = { "datasets": datasets }
}

function search() {
    datasets.value = []
    const wordforms = wordform.value.split(',').map((w) => w.trim())
    wordforms.forEach((w) => getFrequency(w))
}

watch(datasets, () => update(datasets.value), { deep: true })

</script>
<style lang="scss">
.container {
    border: 1px solid gray;
    max-height: 400px;
    max-width: 800px;
    height: 400px;
    width: 800px;
}
</style>
