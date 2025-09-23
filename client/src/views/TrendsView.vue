<template>
    <main>
        <aside>
            <TrendResultsList v-if="trendResults?.length > 0" />
            <Skeleton class="trendlist" v-else-if="trendsLoading" />
            <Panel v-else-if="trendResults?.length == 0" class="trendlist" header="Geen resultaten">
                <p>Probeer een andere zoekopdracht.</p>
            </Panel>
            <div class="settings">
                <TrendSettings />
                <SearchSettings v-if="isValid" />
            </div>
        </aside>
        <GraphWrapper />
    </main>
</template>

<script setup lang="ts">
// Libraries & Stores
import { storeToRefs } from "pinia"
import { useTrendResults } from "@/stores/trendResults"
import { useSearchItems } from "@/stores/searchItems"

// Stores
const { trendResults, trendsLoading } = storeToRefs(useTrendResults())
const { isValid } = storeToRefs(useSearchItems())
</script>

<style scoped lang="scss">
:deep(.trendlist) {
    flex: 1;
}

.settings {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

@media screen and (max-width: 1024px) {
    .trendlist {
        min-height: 500px;
    }
    .settings {
        flex: 1;
    }
}
@media screen and (max-width: 768px) {
    .settings {
        flex: auto;
    }
}
@media screen and (max-width: 480px) {
    .settings {
        gap: 0.5rem;
    }
}
</style>
