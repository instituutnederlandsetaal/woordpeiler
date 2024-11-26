<template>
    <div class="search">
        <TrendSettings />

        <TrendResultsList v-if="trendResults.length != 0" />
        <Skeleton class="trendlist" v-else-if="trendsLoading" />

        <SearchOptionsView />
    </div>
    <D3Graph />
</template>

<script setup lang="ts">
// Libraries & Stores
import { storeToRefs } from "pinia"
import { useTrendResultsStore } from "@/stores/TrendResultsStore"
// Primevue
import Skeleton from "primevue/skeleton"
// Components
import SearchOptionsView from "@/components/SearchSettings.vue"
import TrendSettings from "@/components/trends/TrendSettings.vue"
import D3Graph from "@/components/graph/GraphWrapper.vue"
import TrendResultsList from "@/components/trends/TrendResultsList.vue"

// Stores
const { trendResults, trendsLoading } = storeToRefs(useTrendResultsStore());

</script>

<style scoped lang="scss">
:deep(.trendlist) {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;

    .p-panel-content-container {
        flex: 1;
        min-height: 0;
        display: flex;
        flex-direction: column;

        .p-panel-content {
            flex: 1;
            min-height: 0;
            display: flex;
            flex-direction: column;

            .p-listbox {
                flex: 1;
                min-height: 0;
                display: flex;
                flex-direction: column;
                margin-top: 0.5rem;

                .p-listbox-list-container {
                    flex: 1;
                    max-height: none !important;
                    min-height: 0 !important;
                }
            }
        }
    }
}
</style>