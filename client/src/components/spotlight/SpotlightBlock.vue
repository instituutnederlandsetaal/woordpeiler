<template>
    <section :style="{ backgroundColor: spotlight.color }" @click="search(spotlight.title, spotlight.color)">
        <header>
            <h2>
                {{ spotlight.title }}
            </h2>
        </header>
        <p>sinds {{ spotlight.start_date.split("-")[0] }}</p>
        <div>
            <img :src="svgBlob" />
        </div>
    </section>
</template>

<script setup lang="ts">
// Libraries
import { useRouter } from 'vue-router';
import { onMounted, ref } from "vue";
// API
import * as API from "@/api/search"
import { toTimestamp } from '@/ts/date';
// Types
import { type Spotlight } from "@/types/spotlight";

// Props
const props = defineProps({
    spotlight: {
        type: Object as PropType<Spotlight>,
        required: true
    }
})

// Fields
const router = useRouter()
const svgBlob = ref()

// Methods
function search(word: string, color: string) {
    router.push({ path: '/grafiek', query: { w: word } });
}

// Lifecycle
onMounted(() => {
    const spotlight = props.spotlight
    const request: API.SearchRequest = {
        wordform: spotlight.title,
        start_date: toTimestamp(new Date(spotlight.start_date)),
        period_type: spotlight.period_type || 'week',
        period_length: 1,
    }

    API.getSVG(request)
        .then((response) => {
            const blob = response.data
            console.log(blob)
            svgBlob.value = `data:image/svg+xml;base64,${blob}`
        })
})
</script>

<style scoped lang="scss">
section {
    font-family: 'Schoolboek';
    display: flex;
    flex-direction: column;
    padding: 1rem 2rem;

    header {
        border-bottom: 1px solid black;
    }

    p {
        font-size: 1rem;
        font-weight: 400;
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

    h2 {
        display: inline-block;
        font-size: 2rem;
        font-weight: 400;
        padding-bottom: 0.5rem;
        transition: all 0.15s linear;
    }
}

section:hover,
section:focus {
    cursor: pointer;

    h2 {
        color: white;
    }
}
</style>
