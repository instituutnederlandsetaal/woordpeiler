<template>
    <div class="graph">
        <Panel class="p-panel">

            <!--icons-->
            <template #header v-if="searchResults.length > 0">
                <Button text severity="secondary" @click="downloadBtn">
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
                <!-- <Button text severity="secondary">
                    <span class="pi pi-share-alt" title="Delen"></span>
                </Button> -->
                <div class="panelHeader" style="text-align: center;">
                    <b>{{ graphTitle }}</b>
                </div>
            </template>


            <template v-if="searchResults.length > 0">
                <D3Graph ref="graph" />
            </template>
            <template v-else>
                <ProgressSpinner v-if="isSearching" />
                <div v-else>Zoek een woord</div>
            </template>
        </Panel>
    </div>
</template>

<script setup lang="ts">
// Libraries
import { computed, ref } from "vue";
import { storeToRefs } from "pinia";
// Stores
import { useSearchResultsStore } from "@/stores/SearchResultsStore";
// Components
import D3Graph from "@/components/graph/D3Graph.vue";
// Primevue
import ProgressSpinner from "primevue/progressspinner";
import Panel from "primevue/panel";
import Button from "primevue/button";
// Util
import { download } from "@/ts/saveSvg";

// Stores
const { searchResults, isSearching, lastSearchSettings } = storeToRefs(useSearchResultsStore());

// Fields
const graph = ref(null);
function downloadBtn() {
    download(graph.value.resizeState);
}

// Computed
const graphTitle = computed(() => {
    if (!lastSearchSettings.value) return "";

    const freqType = lastSearchSettings.value.frequencyType === "abs_freq" ? "Absolute" : "Relatieve";
    const timeBucketSize = lastSearchSettings.value.timeBucketSize;
    const timeBucketType = lastSearchSettings.value.timeBucketType;
    let timeBucketStr;
    if (timeBucketType == "month") {
        timeBucketStr = timeBucketSize > 1 ? "maanden" : "maand";
    } else if (timeBucketType == "year") {
        timeBucketStr = timeBucketSize > 1 ? "jaren" : "jaar";
    } else if (timeBucketType == "week") {
        timeBucketStr = timeBucketSize > 1 ? "weken" : "week";
    } else {
        timeBucketStr = timeBucketSize > 1 ? "dagen" : "dag";
    }
    const timeBucket = timeBucketSize > 1 ? `${timeBucketSize} ${timeBucketStr}` : timeBucketStr;

    return `${freqType} woordfrequentie per ${timeBucket}`;
});
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