<template>
    <template v-if="spotlights.length > 1">
        <Carousel class="carousel" :value="spotlights" :numVisible="1" :numScroll="1" circular :autoplayInterval="5000">
            <template #item="slotProps">
                <SpotlightBlock :spotlight="slotProps.data" />
            </template>
        </Carousel>
    </template>
    <SpotlightBlock v-else-if="spotlights[0]" :spotlight="spotlights[0]" />
</template>

<script setup lang="ts">
import type { SpotlightBlock } from "@/types/spotlight"

const { spotlights } = defineProps<{ spotlights: SpotlightBlock[] }>()
</script>
