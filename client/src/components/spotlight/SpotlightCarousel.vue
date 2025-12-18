<template>
    <template v-if="spotlights.length > 1">
        <Carousel class="carousel" :value="spotlights" :numVisible="1" :numScroll="1" circular :autoplayInterval="5000">
            <template #item="slotProps">
                <SpotlightBlock :spotlight="slotProps.data" />
            </template>
        </Carousel>
    </template>
    <div v-else-if="spotlights[0]" class="fake carousel">
        <SpotlightBlock :spotlight="spotlights[0]" />
    </div>
</template>

<script setup lang="ts">
import type { SpotlightBlock } from "@/types/spotlight"

const { spotlights } = defineProps<{ spotlights: SpotlightBlock[] }>()
</script>

<style scoped lang="scss">
.fake {
    padding: 0 2.5rem 1rem 2.5rem;
}
.carousel {
    :deep(.p-icon) {
        width: 1.5rem;
        height: 1.5rem;
    }
    :deep(.p-button) {
        &:hover {
            background: #eee !important;
        }
        &:active {
            background: #ddd !important;
        }
    }
    :deep(.p-carousel-indicator-list) {
        padding-left: 0;
        padding-right: 0;
    }
}
</style>
