<template>
    <SearchBar />
    <main>
        <SpotlightSection v-for="(section, i) in spotlight?.sections" :key="i" :section />
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useSpotlights } from "@/stores/fetch/spotlights"

const { spotlight } = storeToRefs(useSpotlights())
</script>

<style scoped lang="scss">
main {
    padding: 0 1rem;
    gap: 0;
    flex-direction: column;
    min-height: initial;
    align-items: center;
}
</style>
