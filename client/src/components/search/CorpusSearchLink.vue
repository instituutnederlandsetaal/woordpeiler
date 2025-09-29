<template>
    <a v-if="!invalidSearchItem(item)" :href="constructSearchLink(item, searchSettings)" target="_blank">
        {{ searchCorpusText }}
    </a>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { constructSearchLink } from "@/ts/blacklab/blacklab"
import { useSearchSettings } from "@/stores/search/searchSettings"
import { toYear } from "@/ts/date"
import { invalidSearchItem, type SearchItem } from "@/types/search"

const { item } = defineProps<{ item: SearchItem }>()
const { searchSettings } = storeToRefs(useSearchSettings())

const endYear = computed<string>(() => (config.period.end ? ` ${toYear(config.period.end)}` : "nu"))
const searchCorpusText = computed<string>(
    () => `Zoeken in ${config.corpus.name} (${toYear(config.period.start)} – ${endYear.value})`,
)
</script>

<style scoped lang="scss">
a {
    display: block;
    color: blue;
    font-size: 0.9rem;
}
</style>
