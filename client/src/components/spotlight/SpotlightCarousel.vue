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
    padding: 40px;
    padding-top: 0;
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
    article {
        height: 100% !important;
        :deep(figure) {
            min-height: 280px;
        }
    }
    :deep(.p-carousel-content-container) {
        height: 100% !important;
        .p-carousel-content {
            height: 100% !important;
            .p-carousel-item-list {
                height: 100% !important;
            }
        }
    }
}

@media screen and (max-width: 480px) {
    .carousel {
        article {
            :deep(figure) {
                min-height: 150px;
            }
        }
    }
}
</style>
