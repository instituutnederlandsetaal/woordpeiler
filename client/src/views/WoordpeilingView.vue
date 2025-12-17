<template>
    <!-- Woordpeiling: Shows a vertical timeline of the dutch words of the year (per month) -->
    <main>
        <template v-if="woordpeiling">
            <div class="introduction">
                <SpotlightBlock :spotlight="woordpeiling.introduction" />
                <hr />
            </div>
            <!-- The following section must align with no gaps, such that the <hr> (styled to be vertical) align nicely -->
            <template v-for="(wp, i) in woordpeiling.sections" :key="i">
                <section>
                    <!-- carousel of the spotlight graphs of the words of the month -->
                    <div :class="{ left: i % 2, right: (i + 1) % 2 }" v-animateonscroll="{ enterClass: 'appear'}">
                        <template v-if="wp.carousel.length > 1">
                            <Carousel class="carousel" :value="wp.carousel" :numVisible="1" :numScroll="1" circular :autoplayInterval="5000">
                                <template #item="slotProps">
                                    <SpotlightBlock :spotlight="slotProps.data" />
                                </template>
                            </Carousel>
                        </template>
                        <template v-else>
                            <SpotlightBlock :spotlight="wp.carousel[0]" />
                        </template>
                    </div>
                    <!-- decorative vertical line interrupted by the month name -->
                    <div class="timeline">
                        <hr />
                        <h2>{{ wp.timeline }}</h2>
                        <hr />
                    </div>
                    <!-- Editorial article about the words of the month -->
                    <div :class="{ left: (1 + i) % 2, right: i % 2 }" v-animateonscroll="{ enterClass: 'appear'}">
                        <SpotlightBlock :spotlight="wp.article" />
                    </div>
                </section>
            </template>
        </template>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core"
import axios from "axios"
import { type SpotlightGraph } from "@/types/spotlight"

let scrolledToBottom = false

useEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        if (!scrolledToBottom && spotlight.value?.sections) {
            scrolledToBottom = true
            window.plausible("scrolled_to_bottom")
        }
    }
})

type Woordpeiling = {
    introduction: SpotlightBlock,
    sections: {
        timeline: string,
        carousel: SpotlightGraph[]
        article: SpotlightBlock
    }[]
}

const woordpeiling = ref<Woordpeiling>(undefined)
onMounted(() => {
    import("@/assets/woordpeiling.json").then((module) => {
        woordpeiling.value = module.default
    })
})
</script>

<style scoped lang="scss">
main {
    font-size: 1.2rem;
    display: flex;
    flex-direction: column;
    min-height: initial;
    // align-content: stretch;
    gap: 0;
    > .introduction {
        display: flex;
        justify-content: center;
        flex-direction: column;
        align-items: center;
        > hr {
            height: 4rem;
        }
        > article {
            max-width: 600px;
        }
    }
    > section {
        display: flex;
        .left, .right {
            flex: 1 1 0;
            min-width: 0;
            padding: 2rem;
            display: flex;
        }
        .left {
            order: 1;
            justify-content: end;
        }
        .right {
            justify-content: start;
            order: 3;
        }

        > div {
            > .carousel {
                width: 100%;
                max-width: 600px;
                article {
                    width: 100%;
                }
                :deep(.p-icon) {
                    width: 1.5rem;
                    height: 1.5rem;
                }
                :deep(.p-button):hover {
                    background: #eee;
                }
            }
        }
        // Decorative vertical line interrupted by the month name
        // Needs to continuously align with the other sections
        > .timeline {
            display: flex;
            flex-direction: column;
            flex: 0 0 100px;
            align-items: center;
            order: 2;
            // stretch the hr to fill available space
            > hr {
                flex: 1;
            }
            > h2 {
                padding: 0.5rem;
            }
        }
        > div {
            > article {
                max-width: 600px;
            }
        }
    }
}

.appear {
  animation: appear 1s cubic-bezier(0.215, 0.61, 0.355, 1) forwards;
}
@keyframes appear {
  from { opacity: 0; transform: translateY(2rem); }
  to { opacity: 1; transform: none; }
}
</style>
