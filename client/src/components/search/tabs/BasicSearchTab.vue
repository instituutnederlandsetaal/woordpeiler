<template>
    <WordInput :item />
    <LanguageInput :item />
</template>

<script setup lang="ts">
import LanguageInput from "../inputs/LanguageInput.vue"

const { item } = defineProps<{ item: SearchItem }>()
</script>
