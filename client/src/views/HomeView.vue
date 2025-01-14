<template>
    <main>
        <div class="wrapper">
            <SpotlightBlock v-for="spotlight in items" :key="spotlight.word" :spotlight />
        </div>
    </main>
</template>

<script setup lang="ts">
// Libraries
import { storeToRefs } from "pinia"
// Stores
import { useSpotlightStore } from "@/stores/SpotlightStore"
// Components
import SpotlightBlock from "@/components/spotlight/SpotlightBlock.vue"
import { onMounted } from "vue"

// Stores
const spotlightStore = useSpotlightStore()
const { items } = storeToRefs(spotlightStore)
const { fetchSpotlights } = spotlightStore

// Lifecycle
onMounted(() => {
    fetchSpotlights()
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