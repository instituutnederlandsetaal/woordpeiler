<template>
    <div class="graph">
        <div class="p-panel">
            <template v-if="searchResults.length > 0">
                <D3Graph />
            </template>
            <div v-else class="emptyGraph">
                <ProgressSpinner v-if="isSearching" />
                <p v-else>Zoek een woord</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
// Libraries & Stores
import { storeToRefs } from "pinia";
import { useSearchResultsStore } from "@/stores/SearchResultsStore";
// Components
import D3Graph from "@/components/graph/D3Graph.vue";
// Primevue
import ProgressSpinner from "primevue/progressspinner";

// Stores
const { searchResults, isSearching } = storeToRefs(useSearchResultsStore());
</script>