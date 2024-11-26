<template>
    <Panel header="Trendresultaten" class="trendlist">

        <div class="formSplit">
            <label>Uitsluiten</label>
            <MultiSelect v-model="selectedPosHead" display="chip" :options="posHeadOptions" placeholder="Woordsoort"
                :loading="posHeadLoading" style="width:70%;" />
        </div>

        <Listbox class="p-panel" multiple metaKeySelection v-model="selectedTrend" filter :options="filteredTrends"
            optionLabel="wordform">
            <template #option="{ option }">
                <Badge :value="formatNumber(option.keyness)" severity="secondary" />
                &nbsp;
                <span> {{ option.wordform }} </span>
                &nbsp;
                <Chip :label="option.poshead" />
            </template>
        </Listbox>

    </Panel>
</template>

<script setup lang="ts">
// Libraries & Stores
import { ref, computed, watch, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useTrendResultsStore } from '@/stores/TrendResultsStore';
import { useSearchResultsStore } from '@/stores/SearchResultsStore';
import { useSearchItemsStore } from '@/stores/SearchItemsStore';
// Types & API
import type { TrendResult } from '@/types/trends';
import * as ListingAPI from '@/api/listing';
// Primevue
import Listbox from "primevue/listbox"
import Panel from "primevue/panel"
import Chip from "primevue/chip"
import Badge from "primevue/badge"
import MultiSelect from "primevue/multiselect"

import { randomColor } from '@/ts/color';

// Stores
const { trendResults } = storeToRefs(useTrendResultsStore());
const { searchItems } = storeToRefs(useSearchItemsStore());
const { search } = useSearchResultsStore();

// Fields
const selectedTrend = ref<TrendResult[]>([])
/** poshead exclusion */
const selectedPosHead = ref(["nou-p", "res", "num"])
const posHeadOptions = ref<string[]>([])
const posHeadLoading = ref(true)

// Computed
const filteredTrends = computed(() => {
    return trendResults.value.filter((i) => !selectedPosHead.value.includes(i.poshead))
})

// Methods
function formatNumber(num: number): number {
    return Math.floor(num * 10) / 10
}

function getPosHeadOptions() {
    posHeadLoading.value = true
    ListingAPI.getListing("words", "poshead")
        .then((response) => {
            posHeadOptions.value = response.data;
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
    for (const trendItem of selectedTrend.value) {
        searchItems.value.push({
            wordform: trendItem.wordform,
            pos: trendItem.poshead,
            color: randomColor()
        })
    }
    search()
})
</script>
