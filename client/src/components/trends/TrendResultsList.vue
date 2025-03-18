<template>
    <Panel :header="`Trendresultaten: ${displayName(lastTrendSettings)}`" class="trendlist">

        <div class="formSplit" v-if="trendResults[0].poshead">
            <label>Uitsluiten</label>
            <MultiSelect v-model="selectedPosHead" display="chip" :options="posHeadOptions" placeholder="Woordsoort"
                :loading="posHeadLoading" class="posSelect" />
        </div>

        <Listbox multiple metaKeySelection v-model="selectedTrend" filter :options="filteredTrends"
            filterPlaceholder="Zoeken" optionLabel="wordform" :virtualScrollerOptions="{ itemSize: 45 }"
            listStyle="height:100%">
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
// Libraries & Stores
import { ref, computed, watch, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
// Stores
import { useTrendResultsStore } from '@/stores/TrendResultsStore';
import { useSearchResultsStore } from '@/stores/SearchResultsStore';
import { useSearchItemsStore } from '@/stores/SearchItemsStore';
// Types & API
import { type TrendResult, displayName } from '@/types/trends';
import * as ListingAPI from '@/api/listing';
// Primevue
import Listbox from "primevue/listbox"
import Panel from "primevue/panel"
import Chip from "primevue/chip"
import Badge from "primevue/badge"
import MultiSelect from "primevue/multiselect"

import { randomColor } from '@/ts/color';

// Stores
const { trendResults, lastTrendSettings } = storeToRefs(useTrendResultsStore());
const { searchItems } = storeToRefs(useSearchItemsStore());
const { search } = useSearchResultsStore();

// Fields
const selectedTrend = ref<TrendResult[]>([])
/** poshead exclusion */
const selectedPosHead = ref([])
const posHeadOptions = ref<string[]>([])
const posHeadLoading = ref(true)

// Computed
const filteredTrends = computed(() => {
    return trendResults.value?.filter(i => i.poshead?.split(" ")?.every(j => !selectedPosHead.value.includes(j)) || true)
})
const badgeName = computed(() => {
    // key for keyness, freq for frequency
    return lastTrendSettings.value.trendType === 'keyness' ? 'key' : 'freq'
})

// Methods
function formatNumber(num: number): number {
    return Math.floor(num * 10) / 10
}

function getPosHeadOptions() {
    posHeadLoading.value = true
    ListingAPI.getPosheads()
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
            pos: trendItem.pos,
            lemma: trendItem.lemma,
            color: randomColor(),
            visible: true
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

.posSelect {
    flex: 1;
    min-width: 0;
}

.formSplit {
    gap: 1rem;
}

.index {
    font-size: smaller;
}

.trendlist {
    :deep(.p-panel-content) {
        padding: 0 !important;

        .formSplit {
            padding: 0 1rem;
        }

        .p-listbox {
            border: none;

            .p-listbox-header {
                padding-top: 0;
            }

            .p-listbox-list-container {
                padding: 0 0 0 1rem;
            }
        }
    }
}
</style>