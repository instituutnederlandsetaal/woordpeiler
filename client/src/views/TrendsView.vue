<template>
    <main>
        <aside>
            <TrendSettings />

            <TrendResultsList v-if="trendResults?.length > 0" />
            <Skeleton class="trendlist" v-else-if="trendsLoading" />
            <Panel v-else-if="trendResults?.length == 0" class="trendlist" header="Geen resultaten">
                <p>Probeer een andere zoekopdracht.</p>
            </Panel>

            <SearchSettings v-if="isValid" />
        </aside>
        <D3Graph />
    </main>
</template>

<script setup lang="ts">
// Libraries & Stores
import { storeToRefs } from "pinia"
import { useTrendResultsStore } from "@/stores/TrendResultsStore"
import { useSearchItemsStore } from "@/stores/SearchItemsStore"
// Primevue
import Skeleton from "primevue/skeleton"
import Panel from "primevue/panel"
// Components
import SearchSettings from "@/components/SearchSettings.vue"
import TrendSettings from "@/components/trends/TrendSettings.vue"
import D3Graph from "@/components/graph/GraphWrapper.vue"
import TrendResultsList from "@/components/trends/TrendResultsList.vue"
import { onMounted } from "vue"

// Stores
const { trendResults, trendsLoading } = storeToRefs(useTrendResultsStore());
const { isValid } = storeToRefs(useSearchItemsStore());

// Lifecycle
onMounted(() => {
    document.title = "Courantenpeiler - Trends";
});
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

            .formSplit {
                margin-bottom: 0.5rem;
            }

            .p-listbox {
                flex: 1;
                min-height: 0;
                display: flex;
                flex-direction: column;
                overflow: hidden;

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