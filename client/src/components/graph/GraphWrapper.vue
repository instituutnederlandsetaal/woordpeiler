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

<style scoped lang="scss">
.graph {
    flex: 1;

    :deep(.p-panel) {
        height: 100%;
        display: flex;
        flex-direction: column;


        .p-panel-header {
            padding: 0.5rem;
        }

        .p-panel-content-container {
            flex: 1;


            .p-panel-content {
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;


                #svg-container,
                #svg-graph {
                    height: 100%;
                    width: 100%;
                    overflow: visible;
                    padding: 0 1rem 1rem 0.5rem;
                }
            }
        }
    }
}
</style>