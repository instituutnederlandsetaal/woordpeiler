<template>
    <section class="spotlight" :style="{ backgroundColor: spotlight.color }" @click="search(spotlight)">
        <header class="spotlight-header">
            <h2 class="spotlight-title">
                {{ title }}
            </h2>
        </header>
        <div class="spotlight-content">
            <p>
                {{ subtitle }}
            </p>
            <div class="spotlight-link">
                <a
                    v-if="spotlight.articleUrl"
                    :href="spotlight.articleUrl"
                    target="_blank"
                    @click="($event) => $event.stopPropagation()"
                >
                    artikel lezen <span class="pi pi-angle-double-right"></span>
                </a>
            </div>
            <article v-if="spotlight.content" class="spotlight-article">
                <span v-for="(p, i) in spotlight.content" :key="i">
                    {{ p }}
                </span>
            </article>
            <figure v-if="spotlight.graph" class="spotlight-graph">
                <img v-if="svgBlob" :src="svgBlob" />
            </figure>
        </div>
    </section>
</template>

<script setup lang="ts">
// API
import * as API from "@/api/search"
// Types
import type { SpotlightBlock } from "@/types/spotlight"

// Props
const { spotlight } = defineProps<{ spotlight: SpotlightBlock }>()

// Fields
const router = useRouter()
const svgBlob = ref()
const title = computed<string>(() => spotlight.title ?? spotlight.graph?.word ?? spotlight.graph?.lemma)
const subtitle = computed<string>(() => spotlight.subtitle ?? `sinds ${spotlight.graph.start.split("-")[0]}`)

// Methods
function search(spotlight: SpotlightBlock) {
    if (spotlight.content) {
        const params = { w: spotlight.content.join() }
        router.push({ path: "/grafiek", query: params })
        return
    }
    const params = {
        w: spotlight.graph.word,
        l: spotlight.graph.lemma,
        i: spotlight.graph.interval,
        start: spotlight.graph.start,
    }
    router.push({ path: "/grafiek", query: params })
}

// Lifecycle
onMounted(() => {
    if (!spotlight.graph) {
        return
    }
    const graph = spotlight.graph
    const request: API.SearchRequest = {
        wordform: graph.word?.toLowerCase()?.trim(),
        lemma: graph.lemma?.toLowerCase()?.trim(),
        start: graph.start,
        interval: graph.interval,
    }

    API.getSVG(request).then((response) => {
        const blob = response.data
        svgBlob.value = `data:image/svg+xml;base64,${blob}`
    })
})
</script>

<style scoped lang="scss">
.spotlight {
    display: flex;
    flex-direction: column;
    padding: 1rem 2rem;
    cursor: pointer;
    // height
    height: calc(250px + 10vw);
    max-height: 400px;
    max-width: 500px;
    width: 100%;
    // Without this, boxes with long text will grow to max-width, even if the screen is smaller
    overflow: hidden;

    p {
        font-family: "Schoolboek", "Helvetica Neue", Helvetica, Arial, sans-serif;
    }

    &:hover,
    &:focus {
        .spotlight-header .spotlight-title {
            color: white;
        }
    }

    .spotlight-header {
        border-bottom: 1px solid black;

        .spotlight-title {
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
    }

    .spotlight-content {
        display: flex;
        flex-direction: column;
        position: relative;
        min-height: 0;
        flex: 1; // needed on chrome

        .spotlight-link {
            text-align: right;
            position: absolute;
            width: 100%;
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

        .spotlight-article {
            display: flex;
            flex-wrap: wrap;
            line-height: 1rem;
            gap: 0.5rem;
            padding-top: 1rem;
            overflow-y: auto;

            span {
                border: 1px solid black;
                padding: 0.5rem;
            }
        }

        .spotlight-graph {
            flex: 1 0;
            min-height: 0;
            padding-top: 0.3rem;

            img {
                user-select: none;
                height: 100%;
                // strech svg without keeping aspect ratio
                width: 100%;
            }
        }
    }
}
</style>
