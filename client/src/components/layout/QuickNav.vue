<template>
    <nav>
        <a v-for="item in itemsWithIds" :key="item.id" :href="`#${item.id}`">
            {{ item.id?.replace(/-/g, " ") }}
        </a>
    </nav>
</template>

<script setup lang="ts">
import { useSpotlights } from "@/stores/fetch/spotlights"
import type { SpotlightSection } from "@/types/spotlight"

const { spotlight } = storeToRefs(useSpotlights())
const itemsWithIds = computed<SpotlightSection[]>(() => spotlight.value?.sections?.filter((s) => "id" in s) ?? [])
</script>

<style scoped lang="scss">
nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    a {
        color: white;
        background-color: #444;
        padding: 0.5rem 1rem;
        text-decoration: none;
        &:hover {
            text-decoration: underline;
        }
    }
}

@media screen and (max-width: 480px) {
    nav {
        gap: 0.35rem;
        a {
            font-size: 0.85rem;
            padding: 0.35rem 0.65rem;
        }
    }
}
</style>
