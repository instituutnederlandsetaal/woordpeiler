<template>
    <header role="banner">
        <div class="logo">
            <div class="fa fa-4x fa-line-chart" aria-hidden="true"></div>
            <div class="logo-text">
                <h2>/instituut voor de Nederlandse taal/</h2>
                <h1>corpustrends</h1>
            </div>
        </div>
        <nav>
            <a href="/trends">trends</a>
            <a href="/help">help</a>
            <a href="/about">about</a>
        </nav>
    </header>
    <main>
        <div class="search">
            <ScrollPanel class="wordlist">
                <Panel toggleable v-for="dataSerie in dataSeries">
                    <template #header>
                        <ColorPicker id=color v-model="dataSerie.color" />
                        <div class="panelHeader">
                            <template v-if="displayName(dataSerie)"> {{ displayName(dataSerie) }} </template>
                            <template v-else> new word </template>
                        </div>
                    </template>
                    <template #icons>
                        <Button text severity="secondary"
                            @click="() => dataSeries.splice(dataSeries.indexOf(dataSerie), 1)">
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
                        <Select id="pos" v-model="dataSerie.pos" :options="posOptions" showClear
                            placeholder="Part of speech" />
                    </div>
                    <div class="formSplit">
                        <label for="newspaper">Newspaper</label>
                        <Select id="newspaper" v-model="dataSerie.newspaper" :options="newspaperOpts" showClear
                            placeholder="Newspaper" />
                    </div>

                    <!-- </AccordionContent>
                        </AccordionPanel>
                    </Accordion> -->


                </Panel>
                <Button style="border: 2px dashed #ccc; background: #eee; min-height: 40px;" class="newWord"
                    severity="secondary" outlined @click="() => dataSeries.push({ color: randomColor() })">
                    <span class="pi pi-plus"></span> Add
                </Button>
            </ScrollPanel>
            <Panel class="searchOptions">
                <Accordion>
                    <AccordionPanel value="0">
                        <AccordionHeader>
                            Advanced options
                        </AccordionHeader>
                        <AccordionContent class="advancedSearch">
                            <div class="formSplit">
                                <label>Frequency</label>
                                <SelectButton v-model="frequencyType" :options="frequencyTypeOptions"
                                    optionValue="value" optionLabel="label" />
                            </div>
                            <label>Date range</label>
                            <div class="dateRange">
                                <DatePicker v-model="startDate" showIcon fluid iconDisplay="input"
                                    dateFormat="dd-M-yy" />
                                <DatePicker v-model="endDate" showIcon fluid iconDisplay="input" dateFormat="dd-M-yy" />
                            </div>
                            <label>Average over period</label>
                            <div class="timeBucket">
                                <InputNumber v-model="timeBucketSize" inputId="withoutgrouping" :useGrouping="false"
                                    fluid />
                                <SelectButton v-model="timeBucketType" :options="timeBucketOptions" />
                            </div>
                        </AccordionContent>
                    </AccordionPanel>
                </Accordion>
                <Button class="search-btn" label="Search" @click="search" :disabled="dataSeries.length == 0" />
            </Panel>
        </div>
        <div class="graph">
            <Panel header="graph">
                <template #icons>
                    <Button text severity="secondary">
                        <span class="pi pi-download"></span>
                    </Button>
                </template>
                <div v-if="datasets.length === 0" class="emptyGraph">
                    <ProgressSpinner />
                </div>
                <div style="position: relative" v-else>
                    <Line ref=" bar" :data="chartData" :options="chartOptions" />
                </div>

            </Panel>
        </div>
    </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { ChartOptions, ChartData } from 'chart.js';
import { nl } from 'date-fns/locale';
import 'chartjs-adapter-date-fns';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js/auto'
import { Bar, Line } from 'vue-chartjs'
import InputText from 'primevue/inputtext';
import ColorPicker from 'primevue/colorpicker';
import Accordion from 'primevue/accordion';
import AccordionPanel from 'primevue/accordionpanel';
import AccordionHeader from 'primevue/accordionheader';
import AccordionContent from 'primevue/accordioncontent';
import FloatLabel from 'primevue/floatlabel';
import Panel from 'primevue/panel';
import Card from 'primevue/card';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import ScrollPanel from 'primevue/scrollpanel';
import Skeleton from 'primevue/skeleton';
import Select from 'primevue/select';
import SelectButton from 'primevue/selectbutton';
import DatePicker from 'primevue/datepicker';
import InputNumber from 'primevue/inputnumber';
import infixRpnEval from 'infix-rpn-eval';
import { externalTooltipHandler } from '@/js/tooltip.js';

interface DataSeries {
    wordform?: string;
    pos?: string;
    lemma?: string;
    newspaper?: string;
    color?: string;
}

function displayName(str) {
    return Object.entries(str)
        .filter(([key, value]) => value && key !== 'color')
        .map(([key, value]) => value)
        .join(' ')
}

const dataSeries = ref<DataSeries[]>([])




ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
// https://stackblitz.com/github/apertureless/vue-chartjs/tree/main/sandboxes/reactive

const shouldZeroPad = ref(false)
const wordform = ref('')
const datasets = ref([])
const frequencyType = ref("rel_freq")
const frequencyTypeOptions = [{ label: "relative", value: "rel_freq" }, { label: "absolute", value: "abs_freq" }]
const timeBucketSize = ref(1)
const timeBucketType = ref("day")
const timeBucketOptions = ["day", "week", "month", "year"]
const startDate = ref(new Date(new Date().setFullYear(new Date().getFullYear() - 20)))
const endDate = ref(new Date())
const color = ref(null)

const bar = ref(null)
const chartData = ref<ChartData<'line'>>({
    datasets: [
        {
            label: 'lopen',
            data: [{ x: 1619500411 * 1000, y: 40 }, { x: 1719500411 * 1000, y: 20 }],
        },
        {
            label: 'zweven',
            backgroundColor: '#007979',
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
                display: true,
                text: 'Date',
                font: {
                    size: 20,
                },
            },
        },
        y: {
            title: {
                display: true,
                text: 'Frequency (per million words)',
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
                mode: "index"
            },
            enabled: false,
            external: externalTooltipHandler
        },
        // colors: {
        //     forceOverride: true
        // }
    }
})
const styles = ref({
    height: '300px',
    width: '100%',
    position: 'relative',
})

function getFrequency(ds: DataSeries) {
    // param map
    const wordSearch = {
        wordform: ds.wordform,
        poshead: ds.pos,
        lemma: ds.lemma,
        source: ds.newspaper,
    }
    // Remove falsy values, and blank strings (could be tabs and spaces)
    Object.keys(wordSearch).forEach(key => (wordSearch[key] == null || wordSearch[key].trim() === '') && delete wordSearch[key])
    // to string
    const wordSearchString = new URLSearchParams(wordSearch).toString()

    const searchParams = {
        period_length: timeBucketSize.value,
        period_type: timeBucketType.value,
        start_date: startDate.value.getTime() / 1000 | 0,
        end_date: endDate.value.getTime() / 1000 | 0
    }
    const searchParamsString = new URLSearchParams(searchParams).toString()

    // api call
    const url = `http://localhost:8000/word_frequency?${wordSearchString}&${searchParamsString}`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            // data is in the form [{time: 1619500411, value: 40}, {time: 1719500411, value: 20}]
            console.log(color.value)
            const dataset = {
                label: displayName(ds),
                borderColor: `#${ds.color}`,
                backgroundColor: `#${ds.color}`,
                data: data.map((d) => {
                    return { x: d.time * 1000, y: d[frequencyType.value] * 1000000 }
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

function randomColor() {
    return Math.floor(Math.random() * 16777215).toString(16)
}

function search() {
    // save cookies
    localStorage.setItem('dataSeries', JSON.stringify(dataSeries.value))
    datasets.value = []
    dataSeries.value.forEach((ds) => getFrequency(ds))
}

watch(datasets, () => update(datasets.value), { deep: true })

const posOptions = ref([])
onMounted(() => {
    const url = 'http://localhost:8000/ls/words/poshead'
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            posOptions.value = data
        })
})

const newspaperOpts = ref([])
onMounted(() => {
    const url = 'http://localhost:8000/ls/word_frequency/source'
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            newspaperOpts.value = data
        })
})

onMounted(() => {
    // read wordform url parameter
    const urlParams = new URLSearchParams(window.location.search)
    const wordform = urlParams.get('wordform')
    if (wordform) {
        dataSeries.value.push({ wordform: wordform, color: randomColor() })
    } else {
        // retrieve dataseries from cookies
        if (localStorage.getItem('dataSeries')) {
            dataSeries.value = JSON.parse(localStorage.getItem('dataSeries'))
        } else {
            // A random new entry when no cookies were stored
            dataSeries.value.push({ color: randomColor() })
        }
    }
    search()
})

</script>
