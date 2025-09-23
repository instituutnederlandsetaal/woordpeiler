<template>
    <div class="search-items">
        <SearchItem v-for="(item, i) in searchItems" :key="i" :item :collapsed/>
        <Button outlined class="add-btn" severity="secondary" title="Zoekterm toevoegen" @click="add">
            <span class="pi pi-plus"></span>
        </Button>
    </div>
</template>

<script setup lang="ts">
import { useSearchItems } from "@/stores/search/searchItems"
import { useSearchSettings } from "@/stores/search/searchSettings"
import { useSearchResults } from "@/stores/search/searchResults"
import { randomColor } from "@/ts/color"

const searchItemsStore = useSearchItems()
const { searchItems } = storeToRefs(searchItemsStore)
const { readURLParams } = searchItemsStore
const { search } = useSearchResults()
const searchSettingsStore = useSearchSettings()
const { loadSearchSettings } = searchSettingsStore
const collapsed = ref<boolean>(false)

function add() {
    searchItems.value.push({ color: randomColor(), visible: true })
}

// Lifecycle
onMounted(() => {
    // read wordform url parameter
    if (new URLSearchParams(window.location.search).size > 0) {
        readURLParams()
        searchSettingsStore.readUrlParams()
        search()
    } else {
        // retrieve dataseries from cookies
        if (localStorage.getItem("searchItems")) {
            searchItems.value = JSON.parse(localStorage.getItem("searchItems"))
            loadSearchSettings()
            search()
        }
    }
    // if there are more than 3 search items
    // default to collapsed panels
    if (searchItems.value.length > 3) {
        collapsed.value = true
    }
})
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
