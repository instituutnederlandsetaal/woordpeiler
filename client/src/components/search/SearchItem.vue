<template>
    <Panel
        class="search-item"
        :collapsed
        toggleable
        :class="{ invalid: invalidSearchItem(item), hidden: !item.visible }"
    >
        <template #header>
            <div>
                <ColorPicker id="color" v-model="item.color" title="Kleur in grafiek" />
                <Button class="visible-btn" text severity="secondary" @click="item.visible = !item.visible">
                    <span v-if="item.visible" class="pi pi-eye" title="Getoond in grafiek"></span>
                    <span v-else class="pi pi-eye-slash" title="Verborgen in grafiek"></span>
                </Button>
            </div>
            <div class="header">
                <template v-if="displayName(item)">
                    {{ displayName(item) }}
                </template>
                <template v-else><i>lege zoekterm</i></template>
            </div>
        </template>

        <template #toggleicon="data">
            <span v-if="data.collapsed" class="pi pi-chevron-down"></span>
            <span v-else class="pi pi-chevron-up"></span>
        </template>

        <template #icons>
            <span v-if="item.loading">
                <span class="pi pi-spin pi-spinner"></span>
            </span>

            <Button
                text
                severity="secondary"
                @click="() => searchItems.splice(searchItems.indexOf(item), 1)"
                title="Verwijderen"
            >
                <span class="pi pi-trash"></span>
            </Button>
        </template>

        <p class="invalid" v-if="invalidInputText(item.lemma) || invalidInputText(item.wordform)">
            Zoek op maximaal {{ config.search.ngram }} woorden.
        </p>
        <p class="invalid" v-if="invalidRegexUsage(item.lemma) || invalidRegexUsage(item.wordform)">
            Voer minimaal 4 andere tekens in dan een *-joker.
        </p>
        <p class="invalid" v-if="invalidPos(item)">Voer maximaal {{ config.search.ngram }} woordsoorten in.</p>
        <p class="invalid" v-if="invalidTermsForPos(item)">Voer evenveel woorden als woordsoorten in.</p>

        <Tabs value="0">
            <TabList>
                <Tab value="0">Basiszoeken</Tab>
                <Tab value="1">Geavanceerd</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="0" tabindex="-1">
                    <BasicSearchTab :item />
                </TabPanel>
                <TabPanel value="1" tabindex="-1">
                    <AdvancedSearchTab :item />
                </TabPanel>
            </TabPanels>
        </Tabs>

        <a
            v-if="item.wordform && !invalidSearchItem(item)"
            :href="constructSearchLink(item, searchSettings)"
            target="_blank"
        >
            {{ searchCorpusText }}
        </a>
    </Panel>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { constructSearchLink } from "@/ts/blacklab/blacklab"
import { useSearchSettings } from "@/stores/search/searchSettings"
import { useSearchResults } from "@/stores/search/searchResults"
import { useSearchItems } from "@/stores/search/searchItems"
import { toYear } from "@/ts/date"
import {
    displayName,
    invalidSearchItem,
    invalidInputText,
    invalidRegexUsage,
    type SearchItem,
    invalidPos,
    invalidTermsForPos,
} from "@/types/search"

// Props
const { item, collapsed } = defineProps<{ item: SearchItem; collapsed: boolean }>()

// Stores
const { searchItems } = useSearchItems()
const { search } = useSearchResults()
const { searchSettings } = storeToRefs(useSearchSettings())

// Computed
const endYear = computed<string>(() => (config.period.end ? ` ${toYear(config.period.end)}` : "nu"))
const searchCorpusText = computed<string>(
    () => `Zoeken in ${config.corpus.name} (${toYear(config.period.start)} – ${endYear.value})`,
)
</script>

<style scoped lang="scss">
.search-item {
    :deep(.p-panel-header) {
        padding-right: 0.5rem !important;
        .p-panel-header-actions > * {
            padding: 0.5rem;
        }
    }
    .header {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
        flex: 1 1 0;
    }
    :deep(.p-select) {
        width: 200px;
    }
    :deep(.p-inputgroup) {
        .p-select,
        .p-inputtext {
            width: 170px;
        }
    }
    .p-accordionheader {
        padding: 0.65rem 0;
    }
    :deep(.p-tabpanels) {
        padding: 0.5rem 0 0.65rem 0;
    }
    button.p-tab {
        padding: 0.5rem;
    }
    a {
        display: block;
        color: blue;
        // margin: -0.5rem 0;
        font-size: 0.9rem;
    }
    &.hidden {
        filter: brightness(0.9);
    }
    &.invalid {
        border: 2px solid red;
    }
    p.invalid {
        color: red;
        margin-bottom: 0.25rem;
    }
    .visible-btn:focus {
        outline: 1px solid black;
        outline-offset: -3px;
    }
}
</style>
