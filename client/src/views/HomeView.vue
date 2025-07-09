<template>
    <SearchBar />
    <main>
        <SpotlightSection v-for="(section, i) in items" :key="i" :section />
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
// Stores
import { config } from "@/main"
import { useSpotlightStore } from "@/stores/spotlights"

// Stores
const spotlightStore = useSpotlightStore()
const { items } = storeToRefs(spotlightStore)
const { fetchSpotlights } = spotlightStore

// Lifecycle
onMounted(() => {
    fetchSpotlights()
    document.title = config.app.name
})
</script>

<style scoped lang="scss">
main {
    flex-direction: column;
    min-height: initial;
    align-items: center;
    gap: 1rem;
}
</style>
