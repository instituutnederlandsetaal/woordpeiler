<template>
    <Panel class="searchOptions">
        <Accordion>
            <AccordionPanel value="0">
                <AccordionHeader>Zoekinstellingen</AccordionHeader>
                <AccordionContent class="advancedSearch">
                    <div class="formSplit">
                        <label>Frequentie</label>
                        <SelectButton v-model="GraphStore.searchSettings.frequencyType" :options="frequencyTypeOptions"
                            optionValue="value" optionLabel="label" />
                    </div>
                    <label>Periode</label>
                    <div class="dateRange">
                        <DatePicker v-model="GraphStore.searchSettings.startDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                        <DatePicker v-model="GraphStore.searchSettings.endDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                    </div>
                    <label>Gemiddeld over</label>
                    <div class="timeBucket">
                        <InputNumber v-model="GraphStore.searchSettings.timeBucketSize" inputId="withoutgrouping"
                            :useGrouping="false" fluid />
                        <SelectButton v-model="GraphStore.searchSettings.timeBucketType" :options="timeBucketOptions"
                            optionValue="value" optionLabel="label" />
                    </div>
                </AccordionContent>
            </AccordionPanel>
        </Accordion>
        <Button class="search-btn" label="Zoeken" @click="GraphStore.search"
            :disabled="GraphStore.dataSeries.length == 0" />
    </Panel>
</template>

<script setup lang="ts">
import InputText from "primevue/inputtext"
import ColorPicker from "primevue/colorpicker"
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"
import FloatLabel from "primevue/floatlabel"
import Panel from "primevue/panel"
import Card from "primevue/card"
import Button from "primevue/button"
import ProgressSpinner from "primevue/progressspinner"
import ScrollPanel from "primevue/scrollpanel"
import Skeleton from "primevue/skeleton"
import Select from "primevue/select"
import SelectButton from "primevue/selectbutton"
import DatePicker from "primevue/datepicker"
import InputNumber from "primevue/inputnumber"

import { useGraphStore } from "@/store/GraphStore"

const GraphStore = useGraphStore()

const frequencyTypeOptions = [
    { label: "relatief", value: "rel_freq" },
    { label: "absoluut", value: "abs_freq" },
]
const timeBucketOptions = [
    { label: "dag", value: "day" },
    { label: "week", value: "week" },
    { label: "maand", value: "month" },
    { label: "jaar", value: "year" },
]
</script>
