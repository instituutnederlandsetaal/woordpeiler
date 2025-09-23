<template>
    <Panel :header="`Trendresultaten: ${displayName(lastTrendSettings)}`" class="trendlist">
        <fieldset>
            <label>Uitsluiten</label>
            <MultiSelect
                v-model="excludedPos"
                display="chip"
                :options="posOptions"
                placeholder="Woordsoort"
                :loading="!posOptions"
                class="pos-select"
            />
        </fieldset>

        <Listbox
            multiple
            metaKeySelection
            v-model="selectedTrend"
            filter
            :options="filteredTrends"
            filterPlaceholder="Zoeken"
            optionLabel="wordform"
            :virtualScrollerOptions="{ itemSize: 45 }"
            listStyle="flex: 1; display: flex; flex-direction: column"
        >
            <template #option="{ option }">
                <!-- index -->
                <span class="index" title="Rangnummer">{{ trendResults.indexOf(option) + 1 }}.</span>

                &nbsp;
                <span> {{ option.wordform }} </span>
                &nbsp;
                <Chip :label="option.pos" />
                &nbsp;
                <Badge :value="`${badgeName}: ${formatNumber(option.keyness)}`" severity="secondary" />
            </template>
        </Listbox>
    </Panel>
</template>

<script setup lang="ts">
// Stores
import { useTrendResults } from "@/stores/trendResults"
import { useSearchResults } from "@/stores/searchResults"
import { useSearchItems } from "@/stores/searchItems"
// Types & API
import { type TrendResult, displayName } from "@/types/trends"
// Util
import { randomColor } from "@/ts/color"
import { usePosses } from "@/stores/fetch/posses"

// Stores
const { trendResults, lastTrendSettings } = storeToRefs(useTrendResults())
const { searchItems } = storeToRefs(useSearchItems())
const { search } = useSearchResults()

// Fields
const selectedTrend = ref<TrendResult[]>([])
/** poshead exclusion */
const { rawOptions: posOptions } = storeToRefs(usePosses())
const excludedPos = ref<string[]>(["nou-p", "res", "num"])

// Computed
const filteredTrends = computed(() => {
    return trendResults.value?.filter((trend) => {
        const union = new Set(excludedPos.value).intersection(new Set(trend.pos.split(" ")))
        return union.size === 0
    })
})

const badgeName = computed(() => {
    // key for keyness, freq for frequency
    return lastTrendSettings.value.trendType === "keyness" ? "key" : "freq"
})

// Methods
function formatNumber(num: number): number {
    if (num < 1) num = Math.abs(Math.log2(num))
    return Math.floor(num * 10) / 10
}

/** Insert selected trends into search items, and search them. */
watch(selectedTrend, () => {
    searchItems.value = []
    for (const item of selectedTrend.value) {
        searchItems.value.push({
            wordform: item.wordform,
            pos: item.pos,
            lemma: item.lemma,
            color: randomColor(),
            visible: true,
        })
    }
    search()
})
</script>

<style scoped lang="scss">
:deep(.p-chip-label) {
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: smaller;
}

.pos-select {
    flex: 1;
    min-width: 0;
}

.index {
    font-size: smaller;
}

.trendlist {
    display: flex;
    flex-direction: column;
    :deep(.p-panel-content-container) {
        flex: 1;
        display: flex;
        flex-direction: column;
        .p-panel-content {
            padding: 0;
            flex: 1;
            display: flex;
            flex-direction: column;
            fieldset {
                gap: 0.5rem;
                padding: 0 1rem 0.5rem 1rem;
                min-width: 0;
            }
            .p-listbox {
                flex: 1;
                display: flex;
                flex-direction: column;
                border: none;
            }
        }
    }
}
</style>
