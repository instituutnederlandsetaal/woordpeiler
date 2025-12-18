<template>
    <main>
        <section v-for="(section, i) in woordpeiling?.sections ?? []" :key="i">
            <!-- decorative vertical line interrupted by the month name -->
            <div class="middle">
                <template v-if="Array.isArray(section.middle)">
                    <SpotlightCarousel :spotlights="section.middle" />
                </template>
                <template v-else>
                    <hr />
                    <h2>{{ section.middle }}</h2>
                    <hr />
                </template>
            </div>
            <!-- carousel of the spotlight graphs of the words of the month -->
            <div :class="{ left: i % 2, right: (i + 1) % 2 }" v-animateonscroll="{ enterClass: 'appear' }">
                <SpotlightCarousel :spotlights="section.left ?? []" />
            </div>
            <!-- Editorial article about the words of the month -->
            <div :class="{ left: (1 + i) % 2, right: i % 2 }" v-animateonscroll="{ enterClass: 'appear' }">
                <SpotlightCarousel :spotlights="section.right ?? []" />
            </div>
        </section>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core"
import { useWoordpeiling } from "@/stores/fetch/woordpeiling"

const { woordpeiling } = storeToRefs(useWoordpeiling())

let scrolledToBottom = false

useEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        if (!scrolledToBottom && woordpeiling.value?.sections) {
            scrolledToBottom = true
            window.plausible("scrolled_to_bottom")
        }
    }
})
</script>

<style scoped lang="scss">
main {
    font-size: 1.2rem;
    display: flex;
    flex-direction: column;
    min-height: initial;
    // align-content: center;
    gap: 0;
    .skeleton {
        justify-content: center;
    }
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
        .left,
        .right {
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
        > .middle {
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
    from {
        opacity: 0;
        transform: translateY(2rem);
    }
    to {
        opacity: 1;
        transform: none;
    }
}
</style>
