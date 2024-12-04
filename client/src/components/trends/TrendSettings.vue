<template>
    <Accordion :value="tabOpen" class="p-panel" ref="trendAccordion">
        <AccordionPanel value="0">
            <AccordionHeader>Trendinstellingen</AccordionHeader>
            <AccordionContent class="advancedSearch">

                <div class="formSplit">
                    <label>Periode</label>
                    <SelectButton v-model="trendSettings.period" :options="periodOptions" optionValue="value"
                        optionLabel="label" />
                </div>

                <template v-if="trendSettings.period == 'other'">
                    <div class="formSplit">
                        <DatePicker v-model="trendSettings.other.start" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                        <DatePicker v-model="trendSettings.other.end" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                    </div>
                </template>
                <template v-else-if="trendSettings.period == 'year'">
                    <div class="formSplit">
                        <label>Jaar</label>
                        <DatePicker v-model="trendSettings.year.start" view="year" dateFormat="yy"
                            v-on:date-select="setYearEndDate()" />
                    </div>
                </template>
                <template v-else-if="trendSettings.period == 'month'">
                    <div class="formSplit">
                        <label>Maand</label>
                        <DatePicker v-model="trendSettings.month.start" view="month" dateFormat="MM yy"
                            v-on:date-select="setMonthEndDate()" />
                    </div>
                </template>
                <template v-else-if="trendSettings.period == 'week'">
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
import { computed, onMounted, ref, watch } from "vue"
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
const { trendSettings, trendTypeOptions, modifierOptions, periodOptions } = useTrendSettingsStore()
const { getTrends } = useTrendResultsStore()

// Fields
const tabOpen = ref("0")
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
    trendSettings.year.end = toLastDayOfYear(trendSettings.year.start)
}

function setMonthEndDate() {
    trendSettings.month.end = toLastDayOfMonth(trendSettings.month.start)
}

function setWeekCorrectly() {
    // move week.value[0] backwards to the first monday
    week.value[0].setDate(week.value[0].getDate() - week.value[0].getDay())
    // move week.value[1] forwards to the next sunday based on the first monday
    week.value[1] = new Date(week.value[0])
    week.value[1].setDate(week.value[1].getDate() - week.value[1].getDay() + 6)
    // set in settings
    trendSettings.week.start = week.value[0]
    trendSettings.week.end = week.value[1]
}
// Lifecycle
// watch old and new value of period
watch(() => trendSettings.period, (newValue, oldValue) => {
    if (newValue == null) {
        // reset to old
        setTimeout(() => {
            trendSettings.period = oldValue
        }, 0)
    }
})
// same for trendType
watch(() => trendSettings.trendType, (newValue, oldValue) => {
    if (newValue == null) {
        setTimeout(() => {
            trendSettings.trendType = oldValue
        }, 0)
    }
})
onMounted(() => {
    // set initial week
    const oneWeekAgo = new Date()
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
    week.value = [oneWeekAgo, null]
    setWeekCorrectly()
})
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
