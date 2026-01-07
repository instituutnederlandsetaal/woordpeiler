<template>
    <Dialog modal v-model:visible="visible" header="Downloaden">
        <div class="splitter">
            <Panel header="Grafiek">
                <Button severity="secondary" @click="downloadGraph">
                    Grafiek downloaden
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
            </Panel>

            <Panel header="CSV (Excel)">
                <Button severity="secondary">
                    CSV downloaden
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
            </Panel>
        </div>

        <HuisstijlDownload />
    </Dialog>
</template>

<script setup lang="ts">
import { download } from "@/ts/svg/download"
import { useSearchResults } from "@/stores/search/searchResults"

const { searchResults, lastSearchSettings } = storeToRefs(useSearchResults())

const visible = defineModel<boolean>()
const { graph } = defineProps<{ graph: any }>()

function downloadGraph() {
    download(graph.resizeState, searchResults.value, lastSearchSettings.value)
}
</script>

<style scoped lang="scss">
.splitter {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
</style>
