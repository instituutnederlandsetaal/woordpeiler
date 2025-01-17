<template>
    <div class="graph">
        <Panel class="p-panel">

            <!--icons-->
            <template #header v-if="visible.length > 0">
                <Button text severity="secondary" @click="downloadBtn">
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
                <Button text severity="secondary" @click="shareBtn" v-if="canShare">
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
// Components
import D3Graph from "@/components/graph/D3Graph.vue";
// Primevue
import ProgressSpinner from "primevue/progressspinner";
import Panel from "primevue/panel";
import Button from "primevue/button";
// Util
import { share } from "@/ts/svg/share";
import { download } from "@/ts/svg/download";

// Stores
const { searchResults, isSearching, lastSearchSettings } = storeToRefs(useSearchResultsStore());

// Fields
const graph = ref(null);
const canShare = navigator.share != undefined;

// Computed
const visible = computed<GraphItem[]>(() => searchResults.value.filter(d => d.searchItem.visible));

// Methods
function downloadBtn() {
    download(graph.value.resizeState, searchResults.value, lastSearchSettings.value);
}
function shareBtn() {
    share(graph.value.resizeState, searchResults.value, lastSearchSettings.value);
}
</script>

<style scoped lang="scss">
.graph {
    flex: 1 1 0;

    :deep(.p-panel) {
        max-height: 100%;
        height: 100%;

        .p-panel-content-container {
            max-height: 100%;
            height: 100%;

            .p-panel-content {
                max-height: 100%;
                height: 100%;
                padding: 0;

                // Center spinner and help text
                display: flex;
                justify-content: center;
                align-items: center;


                #svg-container {
                    flex: 1;
                    max-height: 100%;
                    height: 100%;
                }
            }
        }

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
    }
}
</style>