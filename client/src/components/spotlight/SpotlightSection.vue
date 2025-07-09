<template>
    <section class="spotlight-section">
        <hgroup class="spotlight-section-header">
            <h2 class="spotlight-section-title">{{ section.title }}</h2>
            <p v-for="(p, i) in section.content" :key="i" v-html="p"></p>
        </hgroup>
        <div class="spotlight-section-content">
            <SpotlightBlock v-for="(block, i) in section.blocks" :key="i" :spotlight="block" />
        </div>
    </section>
</template>

<script setup lang="ts">
import type { SpotlightSection } from "@/types/spotlight"
const { section } = defineProps<{ section: SpotlightSection }>()
</script>

<style scoped lang="scss">
.spotlight-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: calc(4 * 500px + 3 * 1rem);
    width: 100%;

    .spotlight-section-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 0 1rem;

        .spotlight-section-title {
            font-weight: normal;
        }
        p {
            max-width: 1000px;
        }
    }

    .spotlight-section-content {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        grid-gap: 1rem;
        justify-items: center;
    }
}
</style>
