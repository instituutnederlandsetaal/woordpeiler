<template>
    <main>
        <div class="wrapper">
            <SpotlightBlock v-for="spotlight in items" :key="spotlight.word" :spotlight />
        </div>
    </main>
</template>

<script setup lang="ts">
// Stores
import { useSpotlightStore } from "@/stores/spotlights"

// Stores
const spotlightStore = useSpotlightStore()
const { items } = storeToRefs(spotlightStore)
const { fetchSpotlights } = spotlightStore

// Lifecycle
onMounted(() => {
    fetchSpotlights()
    document.title = "Courantenpeiler"
})
</script>

<style scoped lang="scss">
body {
    overflow: auto;
    height: fit-content;
}

.wrapper {
    display: flex;
    flex-wrap: wrap;
    align-content: start;
    justify-content: safe center;
    gap: 1rem;
    margin: 0 auto;
    padding-bottom: 1rem;
    height: fit-content;

    section {
        // height
        height: calc(250px + 10vw);
        max-height: 400px;
        // width
        width: 400px;
        flex-grow: 1;
        max-width: 500px;
        // Without this, boxes with long text will grow to max-width, even if the screen is smaller
        overflow: hidden;
    }
}
</style>
