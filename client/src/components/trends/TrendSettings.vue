<template>
    <Panel class="searchOptions">
        <Accordion :value="tab" ref="trendAccordion">
            <AccordionPanel value="0">
                <AccordionHeader>Trendinstellingen</AccordionHeader>
                <AccordionContent>
                    <Tabs value="0" class="settings">
                        <TabList>
                            <Tab value="0">Woord</Tab>
                            <Tab value="1">Periode</Tab>
                            <Tab value="2">Trend</Tab>
                        </TabList>
                        <TabPanels>
                            <!-- Word tab -->
                            <TabPanel value="0">
                                <div class="formSplit">
                                    <label for="ngram">N-gram</label>
                                    <Select
                                        id="ngram"
                                        v-model="trendSettings.ngram"
                                        :options="ngramOptions"
                                        optionLabel="label"
                                        optionValue="value"
                                        placeholder="N-gram"
                                    />
                                </div>

                                <div class="formSplit">
                                    <label for="variant">Taalvariëteit</label>
                                    <Select
                                        id="variant"
                                        v-model="trendSettings.language"
                                        :options="languageOptions"
                                        showClear
                                        optionLabel="label"
                                        optionValue="value"
                                        placeholder="Taalvariëteit"
                                    />
                                </div>

                                <div class="formSplit">
                                    <label>Verrijkt met woordsoort en lemma</label>
                                    <Checkbox v-model="trendSettings.enriched" binary />
                                </div>
                            </TabPanel>

                            <!-- Period tab -->
                            <TabPanel value="1">
                                <div class="formSplit">
                                    <label>Periode</label>
                                    <SelectButton
                                        v-model="trendSettings.period"
                                        :options="periodOptions"
                                        optionValue="value"
                                        optionLabel="label"
                                    />
                                </div>

                                <template v-if="trendSettings.period == 'other'">
                                    <div class="formSplit">
                                        <label>Vanaf</label>
                                        <DatePicker
                                            v-model="trendSettings.other.start"
                                            showIcon
                                            fluid
                                            iconDisplay="input"
                                            dateFormat="dd-M-yy"
                                        />
                                    </div>
                                    <div class="formSplit">
                                        <label>Tot en met</label>
                                        <DatePicker
                                            v-model="trendSettings.other.end"
                                            showIcon
                                            fluid
                                            iconDisplay="input"
                                            dateFormat="dd-M-yy"
                                        />
                                    </div>
                                </template>
                                <template v-else-if="trendSettings.period == 'year'">
                                    <div class="formSplit">
                                        <label>Jaar</label>
                                        <DatePicker
                                            v-model="trendSettings.year.start"
                                            view="year"
                                            dateFormat="yy"
                                            v-on:date-select="setYearEndDate()"
                                        />
                                    </div>
                                </template>
                                <template v-else-if="trendSettings.period == 'month'">
                                    <div class="formSplit">
                                        <label>Maand</label>
                                        <DatePicker
                                            v-model="trendSettings.month.start"
                                            view="month"
                                            dateFormat="MM yy"
                                            v-on:date-select="setMonthEndDate()"
                                        />
                                    </div>
                                </template>
                                <template v-else-if="trendSettings.period == 'week'">
                                    <div class="formSplit">
                                        <label>Week</label>
                                        <DatePicker
                                            v-model="week"
                                            view="date"
                                            dateFormat="dd M yy"
                                            selectionMode="range"
                                            class="week"
                                            selectOtherMonths
                                            showOtherMonths
                                            :manualInput="false"
                                            v-on:date-select="setWeekCorrectly()"
                                        >
                                        </DatePicker>
                                    </div>
                                </template>
                            </TabPanel>

                            <!-- Trend tab -->
                            <TabPanel value="2">
                                <div class="formSplit">
                                    <label>Trendsoort</label>
                                    <SelectButton
                                        v-model="trendSettings.trendType"
                                        :options="trendTypeOptions"
                                        optionValue="value"
                                        optionLabel="label"
                                    />
                                </div>

                                <div class="formSplit">
                                    <label>{{ modifierLabel }}</label>
                                    <input
                                        type="number"
                                        class="modifierInput p-inputtext"
                                        v-model="trendSettings.modifier"
                                        min="0"
                                    />
                                </div>

                                <!-- <div class="formSplit" v-if="trendSettings.trendType == 'keyness'">
                                    <label>Verdwijnwoorden</label>
                                    <Checkbox v-model="trendSettings.ascending" binary />
                                </div> -->
                            </TabPanel>
                        </TabPanels>
                    </Tabs>

                    <Button
                        class="search-btn"
                        label="Berekenen"
                        @click="
                            () => {
                                tab += 1
                                getTrends()
                            }
                        "
                    />
                </AccordionContent>
            </AccordionPanel>
        </Accordion>
    </Panel>
</template>

<script setup lang="ts">
// Stores
import { useTrendSettingsStore } from "@/stores/trendSettings"
import { useTrendResultsStore } from "@/stores/trendResults"
import { useSearchItemsStore } from "@/stores/searchItems"
// Utils
import { toLastDayOfMonth, toLastDayOfYear } from "@/ts/date"

// Stores
// search items store
const { languageOptions } = useSearchItemsStore()
// trend settings store
const trendSettingsStore = useTrendSettingsStore()
const { trendTypeOptions, modifierOptions, periodOptions, ngramOptions } = trendSettingsStore
const { trendSettings } = storeToRefs(trendSettingsStore)
// trend results store
const { getTrends } = useTrendResultsStore()

// Fields
const tab = ref("0")
const week = ref<Date[]>([])

// Computed
const modifierLabel = computed(() => {
    return modifierOptions[trendSettings.value.trendType]
})

// Methods
function setYearEndDate() {
    trendSettings.value.year.end = toLastDayOfYear(trendSettings.value.year.start)
}

function setMonthEndDate() {
    trendSettings.value.month.end = toLastDayOfMonth(trendSettings.value.month.start)
}

function setWeekCorrectly() {
    // move week.value[0] backwards to the first monday
    week.value[0].setDate(week.value[0].getDate() - week.value[0].getDay())
    // move week.value[1] forwards to the next sunday based on the first monday
    week.value[1] = new Date(week.value[0])
    week.value[1].setDate(week.value[1].getDate() - week.value[1].getDay() + 6)
    // set in settings
    trendSettings.value.week.start = week.value[0]
    trendSettings.value.week.end = week.value[1]
}
// Lifecycle
onMounted(() => {
    // set initial week
    const oneWeekAgo = new Date()
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
    week.value = [oneWeekAgo, null]
    setWeekCorrectly()
})
</script>

<style scoped lang="scss">
.searchOptions {
    :deep(.p-panel-header) {
        display: none !important;
    }

    :deep(.p-panel-content) {
        .p-accordionpanel {
            .p-accordionheader {
                padding-bottom: 0;
            }

            .p-accordioncontent-content {
                padding: 0;
            }

            .p-accordioncontent {
                .p-tab {
                    padding: 0.5rem 0.5rem;
                }

                .p-tabpanels {
                    padding: 0.5rem 0;
                }
            }
        }
    }
}

.modifierInput {
    flex: 1 1 0;
    min-width: 0;
    margin-left: 1rem;
}

.week {
    flex: 1;
    margin-left: 6rem;
}

.formSplit {
    margin-bottom: 0.1rem;
}

.search-btn {
    width: 100%;
}
</style>
