<template>
    <div class="search-items">
        <SearchItem v-for="(item, i) in searchItems" :key="item.uuid" v-model="searchItems[i]" :collapsed />
        <Button outlined class="add-btn" severity="secondary" title="Zoekterm toevoegen" @click="add">
            <span class="pi pi-plus"></span>
        </Button>
    </div>
</template>

<script setup lang="ts">
import { useSearchItems } from "@/stores/search/searchItems"
import { useSearchResults } from "@/stores/search/searchResults"
import { useSearchSettings } from "@/stores/search/searchSettings"
import { randomColor } from "@/ts/color"
import { v4 as uuidv4 } from "uuid"

const { searchItems } = storeToRefs(useSearchItems())
const { searchItemsFromUrl } = useSearchItems()
const { search } = useSearchResults()
const { searchSettingsFromUrl } = useSearchSettings()
const collapsed = ref<boolean>(searchItems.value.length > 3)

function add() {
    searchItems.value.push({ color: randomColor(), visible: true, uuid: uuidv4() })
}

if (new URLSearchParams(window.location.search).size > 0) {
    searchItemsFromUrl()
    searchSettingsFromUrl()
    search()
}
</script>

<style scoped lang="scss">
.search-items {
    min-height: 0;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    padding-bottom: 3rem;
    gap: 1rem;
    flex: 5;

    .add-btn {
        width: 100%;
        border: 2px dashed #ccc !important;
        background: #eee;
        min-height: 40px;

        &:hover,
        &:active {
            background: #e0e0e0 !important;
        }
        &:focus-visible {
            outline-offset: -1px;
        }
    }
}

@media screen and (max-width: 480px) {
    .search-items {
        gap: 0.5rem;
    }
}
</style>
