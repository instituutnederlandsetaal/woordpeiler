<template>
    <SearchBar />
    <main>
        <SpotlightSection v-for="(section, i) in spotlight?.sections" :key="i" :section />
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useSpotlights } from "@/stores/fetch/spotlights"
import { useEventListener } from "@vueuse/core"

const { spotlight } = storeToRefs(useSpotlights())
let scrolledToBottom = false

useEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        if (!scrolledToBottom && spotlight.value?.sections) {
            scrolledToBottom = true
            window.plausible("scrolled_to_bottom")
        }
    }
})
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
