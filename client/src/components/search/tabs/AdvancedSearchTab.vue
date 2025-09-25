<template>
    <LemmaInput :item />
    <PosInput v-model="item.pos" />
    <SourceInput v-if="$internal" :item />
</template>

<script setup lang="ts">
import type { SearchItem } from "@/types/search"

const { item } = defineProps<{ item: SearchItem }>()
</script>
