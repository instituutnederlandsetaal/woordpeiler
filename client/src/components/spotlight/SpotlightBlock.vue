<template>
    <article :style="{ backgroundColor: spotlight.color }">
        <router-link v-if="spotlight.graph || spotlight.words" class="spotlight-link" :to="getGraphUrl(spotlight)" />
        <a
            v-else-if="spotlight.url"
            :href="spotlight.url + '?utm_source=woordpeiler'"
            target="_blank"
            class="spotlight-link"
        />
        <header>
            <h2>{{ title }}</h2>
            <div>
                <p>{{ subtitle }}</p>
                <a
                    v-if="spotlight.url"
                    :href="spotlight.url + '?utm_source=woordpeiler'"
                    target="_blank"
                    @click="(e) => e.stopPropagation()"
                >
                    artikel lezen <span class="pi pi-angle-double-right"></span>
                </a>
            </div>
        </header>
        <div class="spotlight-content">
            <div v-if="spotlight.content">
                <p v-for="(c, i) in spotlight.content" :key="i" v-html="c" />
            </div>
            <hr v-if="spotlight.graph && spotlight.content" />
            <figure v-if="spotlight.graph" v-html="svgBlob" v-intersection-observer="loadSvg" />
            <ul v-if="spotlight.words">
                <li v-for="(w, i) in spotlight.words" :key="i">
                    {{ w }}
                </li>
            </ul>
        </div>
    </article>
</template>

<script setup lang="ts">
import { vIntersectionObserver } from "@vueuse/components"
import * as API from "@/api/search"
import type { SpotlightBlock } from "@/types/spotlight"

// Props
const { spotlight } = defineProps<{ spotlight: SpotlightBlock }>()

// Fields
const svgBlob = ref()
const title = spotlight.title ?? spotlight.graph?.word ?? spotlight.graph?.lemma
const subtitle = spotlight.subtitle ?? (spotlight.graph ? `sinds ${spotlight.graph.start.split("-")[0]}` : "")

// Methods
function getGraphUrl(spotlight: SpotlightBlock): string {
    if (spotlight.words) {
        const params = new URLSearchParams({ w: spotlight.words.join() }).toString()
        return `/grafiek?${params}`
    }
    const params = {
        w: spotlight.graph.word,
        l: spotlight.graph.lemma,
        i: spotlight.graph.interval,
        start: spotlight.graph.start,
    }
    Object.keys(params).forEach((k) => params[k] === undefined && delete params[k])
    return `/grafiek?${new URLSearchParams(params)}`
}

function loadSvg([entry]: IntersectionObserverEntry[]) {
    if (!entry?.isIntersecting || svgBlob.value) {
        return
    }
    const graph = spotlight.graph
    if (!graph) {
        return // not a graph spotlight
    }
    const request: API.SearchRequest = {
        w: graph.word?.toLowerCase()?.trim(),
        l: graph.lemma?.toLowerCase()?.trim(),
        start: graph.start,
        i: graph.interval,
    }

    API.getSVG(request).then((res) => (svgBlob.value = res.data))
}
</script>

<style scoped lang="scss">
article {
    pointer-events: none;
    .spotlight-link {
        position: absolute;
        inset: 0;
        outline-offset: -3px;
    }
    > :not(.spotlight-link) {
        position: relative;
        z-index: 1;
    }
    :deep(a) {
        position: relative;
        pointer-events: auto;
    }
    position: relative;
    color: initial;
    text-decoration: initial;
    display: flex;
    flex-direction: column;
    padding: 1rem 2rem;
    cursor: pointer;
    // height
    min-height: calc(300px + 5vw);
    height: auto;
    // height: 400px;
    // height: ;

    // max-width: 500px;
    // min-width: 100%;
    // Without this, boxes with long text will grow to max-width, even if the screen is smaller
    overflow: hidden;
    gap: 0.5rem;

    &:hover,
    &:focus {
        header h2 {
            text-decoration: underline;
        }
    }

    header {
        h2 {
            border-bottom: 1px solid black;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            display: inline-block;
            min-width: 0;
            font-size: 2rem;
            font-weight: normal;
            padding-bottom: 0.5rem;
            width: 100%;
        }
        div {
            display: flex;
            justify-content: space-between;
            a {
                color: inherit;
                text-decoration: none;

                &:hover {
                    text-decoration: underline;
                }

                span {
                    display: inline;
                    font-size: 0.8rem;
                }
            }
        }
    }

    .spotlight-content {
        display: flex;
        flex-direction: column;
        min-height: 0;
        flex: 1; // needed on chrome
        gap: 0.5rem;
        justify-content: space-between;

        :deep(a) {
            color: black;
            text-decoration: underline;

            &:hover {
                text-decoration: none;
            }
        }

        ul {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            padding: 0;
            border-top: 1px solid black;
            padding-top: 1rem;

            li {
                list-style: none;
                line-height: 1;
                border: 1px solid black;
                padding: 0.5rem;
            }
        }

        figure {
            // flex: 1 0;
            min-height: 0;
            flex: 1 0 calc(100px + 10vw);
            // height: auto;
            // max-height: calc(100px + 10vw);

            :deep(svg) {
                user-select: none;
                height: 100%;
                width: 100%;
                fill: none;
                stroke: black;
                stroke-width: 0.005;
            }
            :deep(svg polyline) {
                stroke-dasharray: 100;
                stroke-dashoffset: 100;
                animation: draw 10s forwards;
            }
            @keyframes draw {
                to {
                    stroke-dashoffset: 0;
                }
            }
        }

        hr {
            width: 100%;
            border: none;
            border-top: 1px solid black;
        }
    }
}

@media screen and (max-width: 1024px) {
    article header h2 {
        font-size: 1.8rem;
    }
}
@media screen and (max-width: 640px) {
    article {
        padding: 0.65rem 1.35rem;

        header {
            h2 {
                font-size: 1.5rem;
            }
            p,
            a {
                font-size: 0.9rem;
            }
        }
        .spotlight-content {
            p {
                font-size: 0.9rem;
            }
            ul {
                padding-top: 0.5rem;
                gap: 0.35rem;
                li {
                    padding: 0.35rem;
                }
            }
        }
    }
}
</style>
