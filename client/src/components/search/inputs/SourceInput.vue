<template>
    <fieldset>
        <label for="source">{{ config.search.filters[1].name }}</label>
        <Select
            id="source"
            :options
            showClear
            v-model="source"
            :clearIconProps="{ tabindex: 0 }"
            :placeholder="config.search.filters[1].name"
            :loading="!options"
        />
    </fieldset>
</template>

<script setup lang="ts">
import { config } from "@/main"
import { useSources } from "@/stores/fetch/sources"

const { options } = storeToRefs(useSources())
const source = defineModel<string>()
</script>
