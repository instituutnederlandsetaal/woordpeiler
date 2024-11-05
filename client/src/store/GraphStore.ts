import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { DataSeries } from "@/ts/DataSeries"
import type { SearchSettings } from "@/ts/SearchSettings"
import { apiURL } from "@/ts/api"


export function displayName(str) {
    return Object.entries(str)
        .filter(([key, value]) => value && key !== "color")
        .map(([key, value]) => value)
        .join(" ")
}

export function randomColor() {
    return Math.floor(Math.random() * 16777215).toString(16)
}

export const useGraphStore = defineStore('GraphStore', () => {
    let datasets = ref({})
    let dataSeries = ref<DataSeries[]>([])
    let searchSettings = ref<SearchSettings>({
        timeBucketType: "year",
        timeBucketSize: 1,
        startDate: new Date('2000-01-01'),
        endDate: new Date(),
        frequencyType: "rel_freq",
    })


    function search() {
        // save cookies
        localStorage.setItem("dataSeries", JSON.stringify(dataSeries.value))
        datasets.value = []
        dataSeries.value.forEach((ds) => getFrequency(ds))
    }

    function getFrequency(ds: DataSeries) {
        // param map
        const wordSearch = {
            wordform: ds.wordform?.trim()?.toLowerCase(),
            pos: ds.pos,
            lemma: ds.lemma,
            source: ds.newspaper,
            language: ds.language
        } 
        
        // Remove falsy values, and blank strings (could be tabs and spaces)
        Object.keys(wordSearch).forEach(
            (key) => (wordSearch[key] == null || wordSearch[key].trim() === "") && delete wordSearch[key]
        )

        // to string
        const wordSearchString = new URLSearchParams(wordSearch).toString()

        const searchParams = {
            period_length: searchSettings.value.timeBucketSize,
            period_type: searchSettings.value.timeBucketType,
            start_date: (searchSettings.value.startDate.getTime() / 1000) | 0,
            end_date: (searchSettings.value.endDate.getTime() / 1000) | 0,
        }
        const searchParamsString = new URLSearchParams(searchParams).toString()

        // api call
        const url = `${apiURL}/word_frequency?${wordSearchString}&${searchParamsString}`
        fetch(url)
            .then((response) => response.json())
            .then((data) => {
                // data is in the form [{time: 1619500411, value: 40}, {time: 1719500411, value: 20}]
                const dataset = {
                    datapoint: ds,
                    label: displayName(ds),
                    borderColor: `#${ds.color}`,
                    backgroundColor: `#${ds.color}`,
                    data: data.map((d) => {
                        return { x: d.time * 1000, y: d[searchSettings.value.frequencyType] * 1000000 }
                    }),
                }
                datasets.value.push(dataset)
            })
    }

    return { datasets, dataSeries, searchSettings, search }
})