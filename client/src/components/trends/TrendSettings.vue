<template>
    <Accordion :value="tabOpen" class="p-panel" ref="trendAccordion">
        <AccordionPanel value="0">
            <AccordionHeader>Trendinstellingen</AccordionHeader>
            <AccordionContent class="advancedSearch">

                <div class="formSplit">
                    <label>Afgelopen</label>
                    <InputNumber class="modifierInput" v-model="trendSettings.periodLength" inputId="withoutgrouping"
                        :useGrouping="false" />
                    <SelectButton v-model="trendSettings.periodType" :options="timeBucketOptions" optionValue="value"
                        optionLabel="label" />
                </div>

                <div class="formSplit">
                    <label>Trendsoort</label>
                    <SelectButton v-model="trendSettings.trendType" :options="trendTypeOptions" optionValue="value"
                        optionLabel="label" />
                </div>

                <div class="formSplit">
                    <label>{{ modifierLabel }}</label>
                    <InputNumber class="modifierInput" v-model="trendSettings.modifier" inputId="withoutgrouping"
                        :useGrouping="false" />
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
import InputNumber from "primevue/inputnumber"

// Stores
const { trendSettings, timeBucketOptions, trendTypeOptions, modifierOptions } = useTrendSettingsStore()
const { getTrends } = useTrendResultsStore()

// Fields
const tabOpen = ref("0")

// Computed
const modifierLabel = computed(() => {
    return modifierOptions[trendSettings.trendType]
})

// Methods
function closeTab() {
    tabOpen.value = ""
}

</script>

<style scoped lang="scss">
.modifierInput {
    flex-basis: 60px;

    :deep(input) {
        width: 100%;
    }
}
</style>
