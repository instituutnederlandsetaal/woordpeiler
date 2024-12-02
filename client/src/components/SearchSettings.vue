<template>
    <Panel class="searchOptions">
        <Accordion>
            <AccordionPanel value="0">
                <AccordionHeader>Zoekinstellingen</AccordionHeader>
                <AccordionContent class="advancedSearch">
                    <div class="formSplit">
                        <label>Frequentie</label>
                        <SelectButton v-model="searchSettings.frequencyType" :options="frequencyTypeOptions"
                            optionValue="value" optionLabel="label" />
                    </div>
                    <label>Periode</label>
                    <div class="dateRange">
                        <DatePicker v-model="searchSettings.startDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                        <DatePicker v-model="searchSettings.endDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                    </div>
                    <label>Gemiddeld over</label>
                    <div class="timeBucket">
                        <InputNumber v-model="searchSettings.timeBucketSize" inputId="withoutgrouping"
                            :useGrouping="false" fluid />
                        <SelectButton v-model="searchSettings.timeBucketType" :options="timeBucketOptions"
                            optionValue="value" optionLabel="label" />
                    </div>
                </AccordionContent>
            </AccordionPanel>
        </Accordion>
        <Button class="search-btn" label="Zoeken" @click="search" :disabled="!isValid" />
    </Panel>
</template>

<script setup lang="ts">
// Libraries & Stores
import { useSearchSettingsStore } from "@/stores/SearchSettingsStore"
import { useSearchResultsStore } from "@/stores/SearchResultsStore"
import { useSearchItemsStore } from "@/stores/SearchItemsStore"
import { storeToRefs } from "pinia"
// Components
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"
import Panel from "primevue/panel"
import Button from "primevue/button"
import SelectButton from "primevue/selectbutton"
import DatePicker from "primevue/datepicker"
import InputNumber from "primevue/inputnumber"

// Stores
const { searchSettings, frequencyTypeOptions, timeBucketOptions } = useSearchSettingsStore()
const { isValid } = storeToRefs(useSearchItemsStore())
const { search } = useSearchResultsStore()
</script>
