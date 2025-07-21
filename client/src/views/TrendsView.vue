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
        <GraphWrapper />
    </main>
</template>

<script setup lang="ts">
// Libraries & Stores
import { storeToRefs } from "pinia"
import { useTrendResultsStore } from "@/stores/trendResults"
import { useSearchItemsStore } from "@/stores/searchItems"
import { config } from "@/main"

// Stores
const { trendResults, trendsLoading } = storeToRefs(useTrendResultsStore())
const { isValid } = storeToRefs(useSearchItemsStore())

// Lifecycle
onMounted(() => {
    document.title = `${config.app.name} - Trends`
})
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
