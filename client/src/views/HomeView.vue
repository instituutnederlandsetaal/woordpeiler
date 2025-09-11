<template>
    <SearchBar />
    <main>
        <SpotlightSection v-for="(section, i) in spotlight.items" :key="i" :section />
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { config } from "@/main"
import { useSpotlightStore } from "@/stores/spotlights"

const spotlight = useSpotlightStore()
document.title = config.app.name
</script>

<style scoped lang="scss">
main {
    flex-direction: column;
    min-height: initial;
    align-items: center;
    gap: 1rem;
}
</style>
