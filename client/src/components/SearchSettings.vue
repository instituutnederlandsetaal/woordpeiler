<template>
    <Panel class="searchOptions">
        <Accordion>
            <AccordionPanel value="0">
                <AccordionHeader>Zoekinstellingen</AccordionHeader>
                <AccordionContent class="advancedSearch">

                    <div class="formSplit" v-if="props.languageSplit">
                        <label>Splits automatisch op taalvariëteit</label>
                        <Checkbox v-model="searchSettings.languageSplit" binary />
                    </div>

                    <div class="formSplit">
                        <label>Frequentie</label>
                        <SelectButton v-model="searchSettings.frequencyType" :options="frequencyTypeOptions"
                            optionValue="value" optionLabel="label" />
                    </div>

                    <div>
                        <label>Periode</label>
                        <Button severity="secondary" text label="Resetten" class="reset" @click="resetDates">
                            <span class="pi pi-refresh"></span> 2000 &ndash; nu
                        </Button>
                    </div>

                    <div class="dateRange">
                        <DatePicker v-model="searchSettings.startDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                        <DatePicker v-model="searchSettings.endDate" showIcon fluid iconDisplay="input"
                            dateFormat="dd-M-yy" />
                    </div>

                    <label>Gemiddeld over</label>
                    <div class="formSplit">
                        <input type="number" class="modifierInput p-inputtext" min="0"
                            v-model="searchSettings.timeBucketSize" />
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
// Libraries
import { storeToRefs } from "pinia"
// Stores
import { useSearchSettingsStore } from "@/stores/SearchSettingsStore"
import { useSearchResultsStore } from "@/stores/SearchResultsStore"
import { useSearchItemsStore } from "@/stores/SearchItemsStore"
// Components
import Accordion from "primevue/accordion"
import AccordionPanel from "primevue/accordionpanel"
import AccordionHeader from "primevue/accordionheader"
import AccordionContent from "primevue/accordioncontent"
import Panel from "primevue/panel"
import Button from "primevue/button"
import SelectButton from "primevue/selectbutton"
import DatePicker from "primevue/datepicker"
import Checkbox from "primevue/checkbox"

// Stores
const searchSettingsStore = useSearchSettingsStore()
const { frequencyTypeOptions, timeBucketOptions, resetDates } = searchSettingsStore
const { searchSettings } = storeToRefs(searchSettingsStore)
const { isValid } = storeToRefs(useSearchItemsStore())
const { search } = useSearchResultsStore()

// Props
const props = defineProps({
    languageSplit: Boolean
})
</script>

<style scoped lang="scss">
.reset {
    display: inline;
    width: fit-content;
    line-height: 0;
    font-size: .9rem;
    margin: 0;
    padding-left: .3rem;

    span {
        font-size: inherit;
    }
}

.modifierInput {
    flex: 0 1 80px;
    min-width: 0;
}
</style>