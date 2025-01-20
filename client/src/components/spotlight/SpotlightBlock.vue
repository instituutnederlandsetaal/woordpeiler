<template>
    <section class="spotlight" :style="{ backgroundColor: spotlight.color }" @click="search(spotlight)">
        <header>
            <h2>
                {{ spotlight.word.toLowerCase().trim() }}
            </h2>
        </header>
        <p>sinds {{ spotlight.start_date.split("-")[0] }}</p>
        <div>
            <img v-if="svgBlob" :src="svgBlob" />
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
function search(spotlight: Spotlight) {
    const params = {
        w: spotlight.word,
        pt: spotlight.period_type,
        ps: spotlight.period_length,
        start: toTimestamp(new Date(spotlight.start_date)),
        end: spotlight.end_date == undefined ? undefined : toTimestamp(new Date(spotlight.end_date)),
    }
    router.push({ path: '/grafiek', query: params });
}

// Lifecycle
onMounted(() => {
    const spotlight = props.spotlight
    const request: API.SearchRequest = {
        wordform: spotlight.word.toLowerCase().trim(),
        start_date: toTimestamp(new Date(spotlight.start_date)),
        period_type: spotlight.period_type,
        period_length: spotlight.period_length,
    }

    API.getSVG(request)
        .then((response) => {
            const blob = response.data
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
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: inline-block;
        min-width: 0;
        font-size: 2rem;
        font-weight: 400;
        padding-bottom: 0.5rem;
        width: 100%;
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
