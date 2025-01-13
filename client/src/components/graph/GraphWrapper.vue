<template>
    <div class="graph">
        <Panel class="p-panel">

            <!--icons-->
            <template #header v-if="visible.length > 0">
                <Button text severity="secondary" @click="downloadBtn">
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
                <Button text severity="secondary" @click="webShareAPI" v-if="canShare">
                    <span class="pi pi-share-alt" title="Delen"></span>
                </Button>
            </template>

            <template v-if="searchResults.length > 0">
                <div v-if="visible.length == 0">
                    Alle woorden zijn verborgen. <br />
                    Toon woorden door op <span class="pi pi-eye-slash"></span> te klikken.
                </div>
                <D3Graph v-else ref="graph" />
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
import { useSearchSettingsStore } from "@/stores/SearchSettingsStore";
// Components
import D3Graph from "@/components/graph/D3Graph.vue";
// Primevue
import ProgressSpinner from "primevue/progressspinner";
import Panel from "primevue/panel";
import Button from "primevue/button";
// Util
import { download, share } from "@/ts/saveSvg";

// Stores
const { searchResults, isSearching, lastSearchSettings } = storeToRefs(useSearchResultsStore());

// Fields
const graph = ref(null);
function downloadBtn() {
    download(graph.value.resizeState);
}
function webShareAPI() {
    share(graph.value.resizeState);
}
const canShare = navigator.share != undefined;

// Computed
const visible = computed<GraphItem[]>(() => searchResults.value.filter(d => d.searchItem.visible));
</script>

<style scoped lang="scss">
.graph {
    flex: 1;
    min-height: inherit;

    :deep(.p-panel) {
        min-height: inherit;
        max-height: inherit;
        display: flex;

        .p-panel-header {
            padding: 0;
            height: 0;
            justify-content: flex-start;
            position: absolute;

            button {
                z-index: 1;
                margin-top: 34px;
            }
        }

        .p-panel-content-container {
            flex: 1;
            display: flex;
            min-height: inherit;
            max-height: inherit;

            .p-panel-content {
                min-height: inherit;
                max-height: inherit;
                flex: 1;


                padding: 0;
                display: flex;
                align-items: center;
                justify-content: center;

                #svg-container,
                #svg-graph {
                    min-height: inherit;
                    max-height: inherit;


                    width: 100%;
                }

                #svg-graph {
                    position: relative;
                }
            }
        }
    }
}
</style>