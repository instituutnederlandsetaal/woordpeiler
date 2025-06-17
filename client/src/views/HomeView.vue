<template>
    <main>
        <SpotlightSection v-for="(section, i) in items" :key="i" :section />
    </main>
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
    display: flex;
    flex-direction: column;
}
</style>
