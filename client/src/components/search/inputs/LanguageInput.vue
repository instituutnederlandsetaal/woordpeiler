<template>
    <fieldset>
        <label for="variant">{{ config.search.filters[0].name }}</label>
        <Select
            id="variant"
            :options
            showClear
            v-model="item.language"
            optionLabel="label"
            optionValue="value"
            :placeholder="config.search.filters[0].name"
            :loading="!options"
        />
    </fieldset>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { useLanguages } from "@/stores/fetch/languages"
const { options } = storeToRefs(useLanguages())
const { item } = defineProps<{ item: SearchItem }>()
</script>
