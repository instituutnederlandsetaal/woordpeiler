<template>
    <main>
        <template v-for="(section, i) in woordpeiling?.sections ?? []" :key="i">
            <section class="content">
                <div class="middle">
                    <template v-if="Array.isArray(section.middle)">
                        <SpotlightCarousel :spotlights="section.middle" />
                        <hr />
                    </template>
                    <template v-else>
                        <hr />
                        <h2 v-if="section.middle" v-html="section.middle" />
                        <hr />
                    </template>
                </div>
                <div v-if="section.left" :class="{ left: i % 2, right: (i + 1) % 2 }" v-intersection-observer="appear">
                    <SpotlightCarousel :spotlights="section.left" />
                </div>
                <div v-if="section.right" :class="{ left: (1 + i) % 2, right: i % 2 }" v-intersection-observer="appear">
                    <SpotlightCarousel :spotlights="section.right" />
                </div>
            </section>
            <section class="divider">
                <div class="middle">
                    <hr />
                </div>
            </section>
        </template>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core"
import { useWoordpeiling } from "@/stores/fetch/woordpeiling"
import { vIntersectionObserver } from "@vueuse/components"

function appear([entry]: IntersectionObserverEntry[]) {
    if (entry?.isIntersecting) {
        const el = entry.target as HTMLElement
        el.classList.add("appear")
    }
}

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
    display: flex;
    flex-direction: column;
    min-height: initial;
    gap: 0;
    section {
        display: flex;
        justify-content: center;
        .left,
        .right {
            flex: 1 1 0;
            min-width: 0;
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
        .middle {
            display: flex;
            flex-direction: column;
            align-items: center;
            order: 2;
            min-width: 150px;
            > h2 {
                text-align: center;
            }
            hr {
                flex: 1;
                &:last-child {
                    padding-top: 2.75rem;
                }
            }
            .carousel.fake {
                padding-bottom: 0;
            }
        }
        .carousel {
            width: 100%;
            max-width: 700px;
        }
    }
    section.divider {
        height: 15rem;
    }
}

.appear {
    animation: appear 1.5s cubic-bezier(0.215, 0.61, 0.355, 1) forwards;
}
.stay {
    opacity: 1;
    transform: none;
}
@keyframes appear {
    from {
        opacity: 0;
        transform: translateY(5rem);
    }
    to {
        opacity: 1;
        transform: none;
    }
}

@media screen and (max-width: 1024px) {
    main {
        padding: 1rem 0;
        section.content {
            flex-direction: column;
            gap: 1rem;
            .left,
            .right {
                justify-content: center;
            }
            .middle {
                order: 0;
                height: 20rem;
                hr {
                    padding: 0 !important;
                }
            }
            .carousel.fake {
                padding-bottom: 0;
            }
        }
        section.divider {
            display: none;
        }
    }
}
</style>
