<template>
    <Panel class="search-settings">
        <Accordion :value="tab">
            <AccordionPanel value="0">
                <AccordionHeader>Zoekinstellingen</AccordionHeader>
                <AccordionContent class="settings">
                    <fieldset>
                        <label>Frequentie</label>
                        <SelectButton
                            v-model="searchSettings.frequencyType"
                            :options="frequencyTypeOptions"
                            optionValue="value"
                            optionLabel="label"
                        />
                    </fieldset>

                    <div>
                        <label>Periode</label>
                        <Button severity="secondary" text label="Resetten" class="reset" @click="resetDates">
                            <span class="pi pi-refresh"></span>
                            <span v-html="periodSpan"></span>
                        </Button>
                    </div>

                    <div class="dateRange">
                        <DatePicker v-model="startDate" showIcon fluid iconDisplay="input" dateFormat="dd-M-yy" />
                        <DatePicker v-model="endDate" showIcon fluid iconDisplay="input" dateFormat="dd-M-yy" />
                    </div>

                    <label>Interval</label>
                    <fieldset>
                        <input type="number" class="p-inputtext" min="1" v-model="searchSettings.intervalLength" />
                        <SelectButton
                            v-model="searchSettings.intervalType"
                            :options="timeBucketOptions"
                            optionValue="value"
                            optionLabel="label"
                        />
                    </fieldset>

                    <fieldset style="margin: 0.2rem 0 -0.2rem 0">
                        <label>Splits automatisch op taalvariëteit</label>
                        <Checkbox v-model="searchSettings.languageSplit" binary />
                    </fieldset>
                </AccordionContent>
            </AccordionPanel>
        </Accordion>

        <Button
            class="search-btn"
            title="Zoeken"
            label="Zoeken"
            @click="
                () => {
                    tab += 1
                    search()
                }
            "
            :disabled="!isValid"
        />
    </Panel>
</template>

<script setup lang="ts">
// Stores
import { useSearchSettingsStore } from "@/stores/searchSettings"
import { useSearchResultsStore } from "@/stores/searchResults"
import { useSearchItemsStore } from "@/stores/searchItems"
// Utils
import { toUTCDate, toYear } from "@/ts/date"
import { config } from "@/main"

// Stores
const searchSettingsStore = useSearchSettingsStore()
const { frequencyTypeOptions, timeBucketOptions, resetDates } = searchSettingsStore
const { searchSettings } = storeToRefs(searchSettingsStore)
const { isValid } = storeToRefs(useSearchItemsStore())
const { search } = useSearchResultsStore()

// Fields
const tab = ref()
// note that these are initialized with the current values from the store, but not reactive by default
const startDate = ref(searchSettings.value.startDate)
const endDate = ref(searchSettings.value.endDate)

// computed
const periodSpan = computed<string>(() => {
    return `${toYear(config.period.start)} &ndash; ${endYear.value}`
})
const endYear = computed<string>(() => {
    return config.period.end ? toYear(config.period.end) : "nu"
})

// Watchers
watch([startDate, endDate], () => {
    // nothing to update
    if (startDate.value === searchSettings.value.startDate && endDate.value === searchSettings.value.endDate) {
        return
    }
    searchSettings.value.startDate = toUTCDate(startDate.value)
    searchSettings.value.endDate = toUTCDate(endDate.value)
})

// reverse
watch(
    () => searchSettingsStore.searchSettings.endDate,
    () => {
        startDate.value = searchSettingsStore.searchSettings.startDate
        endDate.value = searchSettingsStore.searchSettings.endDate
    },
)
</script>

<style scoped lang="scss">
.search-settings {
    height: fit-content;

    :deep(.p-panel-header) {
        display: none !important;
    }
    .search-btn {
        width: 100%;
    }
    .dateRange {
        display: flex;
    }
    .reset {
        display: inline;
        width: fit-content;
        line-height: 0;
        font-size: 0.9rem;

        span {
            font-size: inherit;
            margin-right: 0.25rem;
        }
    }
}
</style>
