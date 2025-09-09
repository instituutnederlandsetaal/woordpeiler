<template>
    <search class="search">
        <h2 class="slogan">{{ $config.app.slogan }}</h2>
        <InputGroup>
            <InputText v-model.trim="word" placeholder="zoeken" @keyup.enter="doSearch" />
            <Button severity="secondary" @click="doSearch" title="Zoeken" icon="pi pi-search" />
        </InputGroup>
        <QuickNav />
    </search>
</template>

<script setup lang="ts">
// Util
import { toTimestamp } from "@/ts/date"


// Fields
const word = ref()
const router = useRouter()

// Methods
function doSearch() {
    router.push({ path: "/grafiek", query: { w: word.value, start: toTimestamp(new Date("1618-01-01")) } })
}
</script>

<style scoped lang="scss">
@use "@/assets/primevue.scss" as *;

.search {
    background-color: $theme;
    width: 100%;
    padding-bottom: .75rem;
    display: flex;
    justify-content: start;
    align-items: center;
    box-shadow: 0px 4px 5px 1px #ccc;
    flex-direction: column;
    gap: .5rem;

    .slogan {
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
            &:focus {
                outline: 1px solid black;
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
            &:focus {
                outline: 1px solid black;
                outline-offset: 0;
            }

            span {
                font-size: 1.2rem;
            }
        }
    }
}
</style>
