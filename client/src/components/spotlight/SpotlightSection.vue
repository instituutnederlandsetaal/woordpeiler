<template>
    <section class="spotlight-section">
        <hgroup class="spotlight-section-header">
            <h2 class="spotlight-section-title">{{ section.title }}</h2>
            <p v-for="(p, i) in section.content" :key="i">
                {{ p }}
            </p>
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
    gap: 0.5rem;
    max-width: calc(4 * 500px + 3 * 1rem);
    width: 100%;

    .spotlight-section-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;

        .spotlight-section-title {
            font-weight: normal;
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
