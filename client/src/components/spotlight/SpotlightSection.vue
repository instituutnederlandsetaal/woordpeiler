<template>
    <section :id="section.id">
        <header v-if="section.title || section.content">
            <h2>{{ section.title }}</h2>
            <p v-for="(p, i) in section.content" :key="i" v-html="p"></p>
        </header>
        <div>
            <SpotlightBlock v-for="(block, i) in section.blocks" :key="i" :spotlight="block" />
        </div>
    </section>
</template>

<script setup lang="ts">
import type { SpotlightSection } from "@/types/spotlight"
const { section } = defineProps<{ section: SpotlightSection }>()

// only navigate to the current anchor after next tick
nextTick(() => {
    const hash = window.location.hash
    if (hash) {
        const el = document.querySelector(hash) as HTMLElement
        if (el) {
            el.scrollIntoView()
        }
    }
})
</script>

<style scoped lang="scss">
section {
    display: flex;
    flex-direction: column;
    // max-width: calc(4 * 500px + 3 * 1rem);
    width: 100%;
    font-family: "Schoolboek", "Helvetica Neue", Helvetica, Arial, sans-serif;
    gap: 1rem;
    padding: 1rem 0;
    border-top: 1px solid #ccc;

    header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;

        h2 {
            font-weight: normal;
        }
        p {
            max-width: 1000px;
        }
    }

    div {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-gap: 1rem;
        // justify-items: center;
    }
}

hr {
    width: 100%;
    border: none;
    border-top: 1px solid #ccc;
    margin: 0.5rem 0;
}

@media screen and (max-width: 1680px) {
    section {
        div {
            grid-template-columns: repeat(3, 1fr);
        }
    }
}

@media screen and (max-width: 1280px) {
    section {
        div {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media screen and (max-width: 768px) {
    section {
        div {
            grid-template-columns: 1fr;
        }
    }
}
</style>
