<template>
    <search>
        <h2>{{ config.app.slogan.toLowerCase() }}</h2>
        <InputGroup>
            <InputText v-model.trim="word" placeholder="zoeken" @keyup.enter="doSearch" />
            <Button severity="secondary" @click="doSearch" title="Zoeken" icon="pi pi-search" />
        </InputGroup>
        <QuickNav />
    </search>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { toTimestamp } from "@/ts/date"

const word = ref()
const router = useRouter()

function doSearch() {
    // example word.value: "mark rutte, geert wilders"
    const props = {
        query: word.value
            .split(",")
            .map((w) => w.trim().toLowerCase())
            .sort()
            .join(","),
    }
    window.plausible("zoekbalk", { props })

    const interval = window.innerWidth < 768 ? config.search.interval.mobile : config.search.interval.desktop
    const intervalStr: string = interval.size + interval.type
    router.push({
        path: "/grafiek",
        query: { i: intervalStr, w: word.value, start: toTimestamp(new Date(config.period.start)) },
    })
}
</script>

<style scoped lang="scss">
@use "@/assets/primevue.scss" as *;

search {
    background-color: $theme;
    width: 100%;
    padding-bottom: 0.75rem;
    display: flex;
    justify-content: start;
    align-items: center;
    box-shadow: 0px 4px 5px 1px #ccc;
    flex-direction: column;
    gap: 0.5rem;
    font-family: "Schoolboek", "Helvetica Neue", Helvetica, Arial, sans-serif;

    h2 {
        font-weight: normal;
        font-size: 1.5rem;
        color: white;
    }

    :deep(.p-inputgroup) {
        width: 90%;
        height: 42px;
        max-width: 400px;

        .p-inputtext {
            font-size: 1.1rem;
            border: 0;
            outline: 0;
            &:focus-visible {
                outline: 2px solid blue;
                outline-offset: 0;
            }
        }

        .p-button {
            border: 0;
            outline: 0;
            padding: 0 1.8rem;
            background-color: #ddd;

            &:hover,
            &:active {
                background-color: #ccc;
            }
            &:focus-visible {
                outline: 2px solid blue;
                outline-offset: 0;
            }

            span {
                font-size: 1.2rem;
            }
        }
    }
}

@media screen and (max-width: 480px) {
    search {
        h2 {
            font-size: 1.3rem;
        }
    }
}
</style>
