<template>
    <section class="spotlight" :style="{ backgroundColor: spotlight.color }" @click="search(spotlight)">
        <header>
            <h2>
                {{ title }}
            </h2>
        </header>
        <div>
            <p>
                sinds
                {{ (spotlight.start ?? spotlight.start_date).split("-")[0] }}
            </p>
            <p v-if="spotlight.articleUrl">
                <a :href="spotlight.articleUrl" target="_blank" @click="($event) => $event.stopPropagation()">
                    lees artikel
                    <span class="pi pi-angle-double-right"></span>&nbsp;</a
                >
            </p>
            <div>
                <img v-if="svgBlob" :src="svgBlob" />
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
// API
import * as API from "@/api/search"
// Types
import { type Spotlight } from "@/types/spotlight"
import { toIntervalStr } from "@/types/search"

// Props
const props = defineProps({ spotlight: { type: Object as PropType<Spotlight>, required: true } })

// Fields
const router = useRouter()
const svgBlob = ref()
const title = computed(() =>
    (props.spotlight.title ?? props.spotlight.word ?? props.spotlight.lemma).toLowerCase().trim(),
)

// Methods
function search(spotlight: Spotlight) {
    const params = {
        w: spotlight.word,
        l: spotlight.lemma,
        i: spotlight.interval ?? toIntervalStr(spotlight.period_type, spotlight.period_length),
        start: spotlight.start ?? spotlight.start_date,
    }
    router.push({ path: "/grafiek", query: params })
}

// Lifecycle
onMounted(() => {
    const spotlight = props.spotlight
    const request: API.SearchRequest = {
        wordform: spotlight.word?.toLowerCase()?.trim(),
        lemma: spotlight.lemma?.toLowerCase()?.trim(),
        start: spotlight.start ?? spotlight.start_date,
        interval: spotlight.interval ?? toIntervalStr(spotlight.period_type, spotlight.period_length),
    }

    API.getSVG(request).then((response) => {
        const blob = response.data
        svgBlob.value = `data:image/svg+xml;base64,${blob}`
    })
})
</script>

<style scoped lang="scss">
section {
    font-family: "Schoolboek";
    display: flex;
    flex-direction: column;
    padding: 1rem 2rem;

    header {
        border-bottom: 1px solid black;

        h2 {
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

    div {
        display: flex;
        flex-direction: column;
        position: relative;
        min-height: 0;

        p {
            font-size: 1rem;
            font-weight: normal;
        }

        /* second p */
        p:nth-of-type(2) {
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
                }
            }
        }

        div {
            flex: 1 0;
            min-height: 0;
            padding-top: 0.3rem;

            img {
                height: 100%;
                // strech svg without keeping aspect ratio
                width: 100%;
            }
        }
    }
}

section:hover,
section:focus {
    cursor: pointer;

    header h2 {
        color: white;
    }
}
</style>
