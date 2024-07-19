<template>
    <input type="text" v-model="chartData.datasets[0].label" />
    <input type="button" value="search" @click="bar.value.update()" />
    <div class="container">
        <Line ref="bar" :data="chartData" :options="chartOptions" :styles />
    </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { ChartOptions, ChartData } from 'chart.js'
import { nl } from 'date-fns/locale';
import 'chartjs-adapter-date-fns';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js/auto'
import { Bar, Line } from 'vue-chartjs'
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
// https://stackblitz.com/github/apertureless/vue-chartjs/tree/main/sandboxes/reactive
const bar = ref(null)
const chartData = ref<ChartData<'line'>>({
    datasets: [
        {
            label: 'lopen',
            data: [{ x: 1619500411 * 1000, y: 40 }, { x: 1719500411 * 1000, y: 20 }],
        },
    ],
})
const chartOptions = ref<ChartOptions<'line'>>({
    locale: 'nl',
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    color: '#0ff',
    backgroundColor: '#f00',
    borderColor: '#0F0',
    scales: {
        // adapters: {
        //     date: {
        //         locale: nl,
        //     },
        // },
        x: {
            type: 'time',
            // time: {
            //     unit: 'day',
            // },
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
})
const styles = ref({
    height: '300px',
    width: '100%',
    position: 'relative',
})
window.onclick = () => {
    // api call
    const url = `http://localhost:8000/word_frequency?poshead=${chartData.value.datasets[0].label}&zero_pad=false`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            // data is in the form [{time: 1619500411, value: 40}, {time: 1719500411, value: 20}]
            chartData.value.datasets[0].data = data.map((d) => {
                return { x: d.time * 1000, y: d.frequency }
            })

            let copy = JSON.parse(JSON.stringify(chartData.value))
            chartData.value = copy
        })


}
</script>
<style lang="scss">
:deep(canvas) {
    max-height: 400px;
    max-width: 400px;
    height: 400px;
    width: 400px;
}

.container {
    border: 10px solid red;
    max-height: 400px;
    max-width: 400px;
    height: 400px;
    width: 400px;
}
</style>
