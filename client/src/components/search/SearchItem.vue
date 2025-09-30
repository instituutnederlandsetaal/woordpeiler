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
                <template v-if="searchToString(item)">
                    {{ searchToString(item) }}
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

        <Tabs :value="tab" @update:value="tabChanged">
            <TabList>
                <Tab value="0">Basiszoeken</Tab>
                <Tab value="1">Geavanceerd</Tab>
            </TabList>
            <TabPanels>
                <TabPanel value="0" tabindex="-1">
                    <SearchItemValidation :item />
                    <BasicSearchTab v-model="basicItem" />
                </TabPanel>
                <TabPanel value="1" tabindex="-1">
                    <AdvancedSearchTab v-model="advancedItem" />
                </TabPanel>
            </TabPanels>
        </Tabs>

        <div class="sources">
            <LanguageInput v-model="item.language" />
            <SourceInput v-if="$internal" v-model="item.source" />
        </div>

        <CorpusSearchLink :item />
    </Panel>
</template>

<script setup lang="ts">
import { useSearchItems } from "@/stores/search/searchItems"
import { invalidSearchItem, searchToString, type SearchItem } from "@/types/search"

const { collapsed } = defineProps<{ collapsed: boolean }>()
const { searchItems } = storeToRefs(useSearchItems())

const tab = ref<string>("0")

const item = defineModel<SearchItem>()
const basicItem = ref<SearchItem>({
    terms: (() => {
        const terms = structuredClone(toRaw(item.value?.terms))
            ?.map((t) => ({ ...t, lemma: undefined, pos: undefined }))
            .filter((t) => Object.values(t).filter(Boolean).length)
        return terms && terms.length ? terms : undefined
    })(),
})
const advancedItem = ref<SearchItem>({ terms: structuredClone(toRaw(item.value?.terms)) })

watch(
    basicItem,
    (newVal) => {
        item.value = { ...item.value, ...newVal }
    },
    { deep: true },
)

watch(
    advancedItem,
    (newVal) => {
        item.value = { ...item.value, ...newVal }
    },
    { deep: true },
)

onMounted(() => {
    // if the current item contains advanced fields, switch to advanced tab
    if (item.value?.terms?.some((t) => t.lemma !== undefined || t.pos !== undefined)) {
        tab.value = "1"
    }
})

function tabChanged(value: string) {
    if (value === "0") {
        // switch to basic tab
        const override = { ...item.value, ...basicItem.value }
        item.value = override
    } else {
        // switch to advanced tab
        item.value = { ...item.value, ...advancedItem.value }
    }
}
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
    &.hidden {
        filter: brightness(0.9);
    }
    &.invalid {
        border: 2px solid red;
    }
    .visible-btn:focus-visible {
        outline: 2px solid blue;
        outline-offset: -3px;
    }
}
.sources {
    margin-bottom: 0.5rem;
}
</style>
