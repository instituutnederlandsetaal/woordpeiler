<template>
    <Panel :header="`Trendresultaten: ${displayName(lastTrendSettings)}`" class="trendlist">
        <fieldset>
            <label>Uitsluiten</label>
            <MultiSelect
                v-model="excludedPosHead"
                display="chip"
                :options="posHeadOptions"
                placeholder="Woordsoort"
                :loading="posHeadLoading"
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
                <Chip :label="option.poshead" v-if="option.poshead" />
                &nbsp;
                <Badge :value="`${badgeName}: ${formatNumber(option.keyness)}`" severity="secondary" />
            </template>
        </Listbox>
    </Panel>
</template>

<script setup lang="ts">
// Stores
import { useTrendResultsStore } from "@/stores/trendResults"
import { useSearchResultsStore } from "@/stores/searchResults"
import { useSearchItemsStore } from "@/stores/searchItems"
import { useTrendSettingsStore } from "@/stores/trendSettings"
// Types & API
import { type TrendResult, displayName } from "@/types/trends"
import * as ListingAPI from "@/api/listing"
// Util
import { randomColor } from "@/ts/color"

// Stores
const { trendResults, lastTrendSettings } = storeToRefs(useTrendResultsStore())
const { searchItems } = storeToRefs(useSearchItemsStore())
const { excludedPosHead } = storeToRefs(useTrendSettingsStore())
const { search } = useSearchResultsStore()

// Fields
const selectedTrend = ref<TrendResult[]>([])
/** poshead exclusion */
const posHeadOptions = ref<string[]>([])
const posHeadLoading = ref(true)

// Computed
const filteredTrends = computed(() => trendResults.value?.filter((i) => !excludedPosHead.value.includes(i.poshead)))
const badgeName = computed(() => {
    // key for keyness, freq for frequency
    return lastTrendSettings.value.trendType === "keyness" ? "key" : "freq"
})

// Methods
function formatNumber(num: number): number {
    if (num < 1) num = Math.abs(Math.log2(num))
    return Math.floor(num * 10) / 10
}

function getPosHeadOptions() {
    posHeadLoading.value = true
    ListingAPI.getPosheads()
        .then((response) => {
            posHeadOptions.value = response.data
        })
        .finally(() => {
            posHeadLoading.value = false
        })
}

// Lifecycle
onMounted(() => {
    getPosHeadOptions()
})

/** Insert selected trends into search items, and search them. */
watch(selectedTrend, () => {
    searchItems.value = []
    const isWordform = lastTrendSettings.value.enriched

    for (const trendItem of selectedTrend.value) {
        searchItems.value.push({
            wordform: isWordform ? trendItem.wordform : undefined,
            pos: trendItem.pos,
            lemma: isWordform ? trendItem.lemma : trendItem.wordform,
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
