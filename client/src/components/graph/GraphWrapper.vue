<template>
    <figure>
        <Panel class="p-panel">
            <!--icons-->
            <template #header v-if="visible.length > 0">
                <Button text severity="secondary" @click="downloadBtn">
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
                <Button text severity="secondary" @click="shareBtn" v-if="canShare">
                    <span class="pi pi-share-alt" title="Delen"></span>
                </Button>
                <Button text severity="secondary" @click="resetZoom" v-if="zoomedIn">
                    <span class="pi pi-search-minus" title="Uitzoomen"></span>
                </Button>
            </template>

            <template v-if="searchResults.length > 0">
                <div v-if="visible.length == 0">
                    Alle woorden zijn verborgen. <br />
                    Toon woorden door op
                    <span class="pi pi-eye-slash"></span> te klikken.
                </div>
                <D3Graph v-else ref="graph" />
            </template>
            <template v-else>
                <ProgressSpinner v-if="isSearching" animationDuration=".5s" />
                <div v-else>Zoek een woord</div>
            </template>
        </Panel>
    </figure>
</template>

<script setup lang="ts">
// Stores
import { useSearchResults } from "@/stores/search/searchResults"
// Util
import { share } from "@/ts/svg/share"
import { download } from "@/ts/svg/download"

// Stores
const { searchResults, isSearching, lastSearchSettings } = storeToRefs(useSearchResults())

// Fields
const graph = ref(null)
const canShare = navigator.share != undefined

// Computed
const visible = computed<GraphItem[]>(() => searchResults.value.filter((d) => d.searchItem.visible))
const zoomedIn = computed(() => graph.value?.zoomedIn)

// Methods
function downloadBtn() {
    download(graph.value.resizeState, searchResults.value, lastSearchSettings.value)
}
function shareBtn() {
    share(graph.value.resizeState, searchResults.value, lastSearchSettings.value)
}

function resetZoom() {
    graph.value.resetZoom()
}
</script>

<style scoped lang="scss">
figure {
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

@media screen and (max-width: 1024px) {
    figure {
        min-height: 500px;
        height: 500px;
    }
}
@media screen and (max-width: 768px) {
    figure {
        min-height: 400px;
        height: 400px;
    }
}
@media screen and (max-width: 480px) {
    figure {
        min-height: 350px;
        height: 350px;
        margin-top: 30px;

        :deep(.p-panel) {
            .p-panel-header {
                box-sizing: border-box !important;
                background-color: white;
                height: 30px !important;
                margin-top: -30px;
                position: static;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                margin-left: -1px !important;
                position: absolute;

                .p-button {
                    height: 100%;
                    margin: 0 !important;
                }
            }
        }
    }
}
</style>
