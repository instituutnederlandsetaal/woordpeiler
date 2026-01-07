<template>
    <fieldset>
        <input type="number" class="p-inputtext" min="1" v-model="intervalLength" />
        <SelectButton v-model="intervalType" :options="intervalTypes" optionValue="value" optionLabel="label" />
    </fieldset>
</template>

<script setup lang="ts">
import type { SelectLabel } from "@/types/ui"

const intervalLength = ref<number>(3)
const intervalTypes: SelectLabel[] = [
    { label: "dag", value: "d" },
    { label: "week", value: "w" },
    { label: "maand", value: "m" },
    { label: "jaar", value: "y" },
]
const intervalType = ref<string>(intervalTypes[2].value)
const interval = computed<string>(() => `${intervalLength.value}${intervalType.value}`)
const model = defineModel<string>()
watch(interval, () => (model.value = interval.value), { immediate: true })
</script>
