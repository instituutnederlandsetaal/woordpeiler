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
        title: "europapa",
        color: "#359FF0",
        start_date: "2024-01-01"
    },
    {
        title: "graaiflatie",
        color: "#BD795D",
        start_date: "2023-01-01"
    },
    {
        title: "corona",
        color: "#FFF064",
        start_date: "2020-01-01"
    },
    {
        title: "smartphone",
        color: "#89C24B",
        start_date: "2006-01-01",
        period_type: "month",
    },
    {
        title: "tsunami",
        color: "#FF8000",
        start_date: "2000-01-01",
        period_type: "month",
    },
    {
        title: "tiktok",
        color: "#E8503D",
        start_date: "2018-01-01",
        period_type: "month",
    },
    {
        title: "knuffelcontact",
        color: "#359FF0",
        start_date: "2020-01-01",
        period_type: "week",
    },
    {
        title: "omtzigt",
        color: "#BD795D",
        start_date: "2020-01-01",
        period_type: "week",
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
        width: 400px;
        height: 350px;
    }
}
</style>