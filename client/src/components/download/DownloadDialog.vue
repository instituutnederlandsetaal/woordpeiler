<template>
    <Dialog modal v-model:visible="visible" header="Downloaden">
        <div class="splitter">
            <Panel header="Grafiek">
                <Button severity="secondary" @click="downloadSvg(graph.resizeState, searchResults, lastSearchSettings)">
                    Grafiek downloaden
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
            </Panel>

            <Panel header="CSV (Excel)">
                <Button severity="secondary" @click="downloadCsv(searchResults)">
                    CSV downloaden
                    <span class="pi pi-download" title="Downloaden"></span>
                </Button>
            </Panel>
        </div>

        <HuisstijlDownload />
    </Dialog>
</template>

<script setup lang="ts">
import { download as downloadSvg } from "@/ts/svg/download"
import { download as downloadCsv } from "@/ts/csv/download"
import { useSearchResults } from "@/stores/search/searchResults"

const { searchResults, lastSearchSettings } = storeToRefs(useSearchResults())

const visible = defineModel<boolean>()
const { graph } = defineProps<{ graph: any }>()
</script>

<style scoped lang="scss">
.splitter {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}
</style>
