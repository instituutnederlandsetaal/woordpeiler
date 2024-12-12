<template>
    <main>
        <div class="wrapper">
            <SpotlightBlock v-for="spotlight in data" :key="spotlight.title" :spotlight />
        </div>
    </main>
</template>

<script setup lang="ts">
import SpotlightBlock from "@/components/spotlight/SpotlightBlock.vue"
import { ref } from "vue";
import { type Spotlight } from "@/types/spotlight";

const data = ref<Spotlight[]>([
    {
        title: "trump",
        color: "#FF8000",
        start_date: "2000-01-01",
        period_type: "month",
        period_length: 1,
        interval: '1m'
    },
    {
        title: "krim",
        color: "#9977FF",
        start_date: "2013-01-01",
        period_type: "week",
        period_length: 2,
    },
    {
        title: "trump",
        color: "#FFF064",
        start_date: "2014-01-01",
        period_type: "month",
    },
    {
        title: "europapa",
        color: "#359FF0",
        start_date: "2024-01-01",
        period_type: "week",
        period_length: 1,
    },
    {
        title: "graaiflatie",
        color: "#BD795D",
        start_date: "2023-01-01",
        period_type: "week",
        period_length: 1,
    },
    {
        title: "smartphone",
        color: "#89C24B",
        start_date: "2006-01-01",
        period_type: "month",
        period_length: 3,
    },
    {
        title: "tiktok",
        color: "#E8503D",
        start_date: "2018-01-01",
        period_type: "month",
        period_length: 1,

    },
    {
        title: "knuffelcontact",
        color: "#359FF0",
        start_date: "2020-01-01",
        period_type: "week",
        period_length: 1,

    },
    {
        title: "vapen",
        color: "#FF8000",
        start_date: "2018-01-01",
        period_type: "week",
        period_length: 3,
    },
    {
        title: "knaldrang",
        color: "#FFF064",
        start_date: "2020-01-01",
        period_type: "week",
        period_length: 2,
    },
    {
        title: "menstruatieproducten",
        color: "#E8503D",
        start_date: "2018-01-01",
        period_type: "month",
        period_length: 1,
    },
    {
        title: "klimaatspijbelaars",
        color: "#89C24B",
        start_date: "2018-01-01",
        period_type: "month",
        period_length: 1,
    },
    {
        title: "stikstofcrisis",
        color: "#BD795D",
        start_date: "2018-01-01",
        period_type: "month",
        period_length: 1,
    }
])
</script>

<style scoped lang="scss">
body {
    overflow: auto;
    height: fit-content;
}

.wrapper {
    display: flex;
    flex-wrap: wrap;
    align-content: start;
    justify-content: safe center;
    gap: 1rem;
    margin: 0 auto;
    padding-bottom: 1rem;
    height: fit-content;

    section {
        // height
        height: calc(300px + 3vw);
        max-height: 400px;
        // width
        width: 400px;
        flex-grow: 1;
        max-width: 500px;
    }
}
</style>