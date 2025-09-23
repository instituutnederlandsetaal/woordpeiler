<template>
    <Panel class="trend-settings">
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
                                <fieldset>
                                    <label for="ngram">N-gram</label>
                                    <Select
                                        id="ngram"
                                        v-model="trendSettings.ngram"
                                        :options="ngramOptions"
                                        optionLabel="label"
                                        optionValue="value"
                                        placeholder="N-gram"
                                    />
                                </fieldset>

                                <fieldset>
                                    <label for="variant">{{ config.search.filters[0].name }}</label>
                                    <Select
                                        id="variant"
                                        v-model="trendSettings.language"
                                        :options="languageOptions"
                                        showClear
                                        :loading="!languageOptions"
                                        optionLabel="label"
                                        optionValue="value"
                                        :placeholder="config.search.filters[0].name"
                                    />
                                </fieldset>
                            </TabPanel>

                            <!-- Period tab -->
                            <TabPanel value="1">
                                <fieldset>
                                    <label>Periode</label>
                                    <SelectButton
                                        v-model="trendSettings.period"
                                        :options="periodOptions"
                                        optionValue="value"
                                        optionLabel="label"
                                    />
                                </fieldset>

                                <template v-if="trendSettings.period == 'other'">
                                    <fieldset>
                                        <label>Vanaf</label>
                                        <DatePicker
                                            v-model="trendSettings.other.start"
                                            showIcon
                                            fluid
                                            iconDisplay="input"
                                            dateFormat="dd-M-yy"
                                        />
                                    </fieldset>
                                    <fieldset>
                                        <label>Tot en met</label>
                                        <DatePicker
                                            v-model="trendSettings.other.end"
                                            showIcon
                                            fluid
                                            iconDisplay="input"
                                            dateFormat="dd-M-yy"
                                        />
                                    </fieldset>
                                </template>
                                <template v-else-if="trendSettings.period == 'year'">
                                    <fieldset>
                                        <label>Jaar</label>
                                        <DatePicker
                                            v-model="trendSettings.year.start"
                                            view="year"
                                            dateFormat="yy"
                                            v-on:date-select="setYearEndDate()"
                                        />
                                    </fieldset>
                                </template>
                                <template v-else-if="trendSettings.period == 'month'">
                                    <fieldset>
                                        <label>Maand</label>
                                        <DatePicker
                                            v-model="trendSettings.month.start"
                                            view="month"
                                            dateFormat="MM yy"
                                            v-on:date-select="setMonthEndDate()"
                                        />
                                    </fieldset>
                                </template>
                                <template v-else-if="trendSettings.period == 'week'">
                                    <fieldset>
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
                                    </fieldset>
                                </template>
                            </TabPanel>

                            <!-- Trend tab -->
                            <TabPanel value="2">
                                <fieldset>
                                    <label>Trendsoort</label>
                                    <SelectButton
                                        v-model="trendSettings.trendType"
                                        :options="trendTypeOptions"
                                        optionValue="value"
                                        optionLabel="label"
                                    />
                                </fieldset>

                                <fieldset>
                                    <label>{{ modifierLabel }}</label>
                                    <input type="number" class="p-inputtext" v-model="trendSettings.modifier" min="0" />
                                </fieldset>
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
import { useTrendSettings } from "@/stores/trends/trendSettings"
import { useTrendResults } from "@/stores/trends/trendResults"
// Utils
import { toLastDayOfMonth, toLastDayOfYear } from "@/ts/date"
import { useLanguages } from "@/stores/fetch/languages"
import { config } from "@/main"

// Stores
const { options: languageOptions } = storeToRefs(useLanguages())
const { trendSettings } = storeToRefs(useTrendSettings())
const { trendTypeOptions, modifierOptions, periodOptions, ngramOptions } = useTrendSettings()
const { getTrends } = useTrendResults()

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
.trend-settings {
    height: fit-content;

    :deep(.p-panel-header) {
        display: none !important;
    }

    :deep(.p-panel-content) {
        .p-select {
            width: 200px;
        }

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

    .week {
        flex: 1;
        margin-left: 6rem;
    }

    .search-btn {
        width: 100%;
    }
}
</style>
