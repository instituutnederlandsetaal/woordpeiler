<template>
    <Accordion :value="tabOpen" class="p-panel" ref="trendAccordion">
        <AccordionPanel value="0">
            <AccordionHeader>Trendinstellingen</AccordionHeader>
            <AccordionContent class="advancedSearch">

                <div class="formSplit">
                    <label>Periode</label>
                    <SelectButton v-model="selectedPeriod" :options="periodOptions" optionValue="value"
                        optionLabel="label" />
                </div>

                <template v-if="selectedPeriod == 'other'">
                    <div class="formSplit">
                        <DatePicker v-model="trendSettings.startDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                        <DatePicker v-model="trendSettings.endDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                    </div>
                </template>
                <template v-else-if="selectedPeriod == 'year'">
                    <div class="formSplit">
                        <label>Jaar</label>
                        <DatePicker v-model="trendSettings.startDate" view="year" dateFormat="yy"
                            v-on:date-select="setYearEndDate()" />
                    </div>
                </template>
                <template v-else-if="selectedPeriod == 'month'">
                    <div class="formSplit">
                        <label>Maand</label>
                        <DatePicker v-model="trendSettings.startDate" view="month" dateFormat="MM yy"
                            v-on:date-select="setMonthEndDate()" />
                    </div>
                </template>
                <template v-else-if="selectedPeriod == 'week'">
                    <div class="formSplit">
                        <label>Week</label>
                        <DatePicker v-model="week" view="date" dateFormat="dd M yy" selectionMode="range" class="week"
                            selectOtherMonths showOtherMonths :manualInput="false"
                            v-on:date-select="setWeekCorrectly()">
                        </DatePicker>
                    </div>
                </template>

                <div class="formSplit">
                    <label>Trendsoort</label>
                    <SelectButton v-model="trendSettings.trendType" :options="trendTypeOptions" optionValue="value"
                        optionLabel="label" />
                </div>

                <div class="formSplit">
                    <label>{{ modifierLabel }}</label>
                    <input type="number" class="modifierInput p-inputtext" v-model="trendSettings.modifier" min="0" />
                </div>

                <Button class="search-btn" label="Berekenen" @click="() => { closeTab(); getTrends(); }" />

            </AccordionContent>
        </AccordionPanel>
    </Accordion>
</template>

<script setup lang="ts">
// Libraries & Stores
import { computed, ref } from "vue"
import { useTrendSettingsStore } from "@/stores/TrendSettingsStore"
import { useTrendResultsStore } from "@/stores/TrendResultsStore"
// Primevue
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"
import Button from "primevue/button"
import SelectButton from "primevue/selectbutton"
import DatePicker from "primevue/datepicker"
import { toLastDayOfMonth, toLastDayOfYear } from "@/ts/date"

// Stores
const { trendSettings, trendTypeOptions, modifierOptions } = useTrendSettingsStore()
const { getTrends } = useTrendResultsStore()

// Fields
const tabOpen = ref("0")
const periodOptions: SelectLabel[] = [
    { label: "week", value: "week" },
    { label: "maand", value: "month" },
    { label: "jaar", value: "year" },
    { label: "anders", value: "other" },
]
const selectedPeriod = ref("year")
const week = ref<Date[]>([])

// Computed
const modifierLabel = computed(() => {
    return modifierOptions[trendSettings.trendType]
})

// Methods
function closeTab() {
    tabOpen.value = parseInt(tabOpen.value) + 1
}

function setYearEndDate() {
    trendSettings.endDate = toLastDayOfYear(trendSettings.startDate)
}

function setMonthEndDate() {
    trendSettings.endDate = toLastDayOfMonth(trendSettings.startDate)
}

function setWeekCorrectly() {
    // move week.value[0] backwards to the first monday
    week.value[0].setDate(week.value[0].getDate() - week.value[0].getDay())
    // move week.value[1] forwards to the next sunday based on the first monday
    week.value[1] = new Date(week.value[0])
    week.value[1].setDate(week.value[1].getDate() - week.value[1].getDay() + 6)
    // set in settings
    trendSettings.startDate = week.value[0]
    trendSettings.endDate = week.value[1]
}

</script>

<style scoped lang="scss">
.modifierInput {
    flex: 1 1 0;
    min-width: 0;
    margin-left: 1rem;
}

.week {
    flex: 1;
    margin-left: 6rem;
}
</style>
