<template>
    <nav>
        <a v-for="item in itemsWithIds" :key="item.id" :href="`#${item.id}`">{{ item.title }}</a>
    </nav>
</template>

<script setup lang="ts">
import { useSpotlightStore } from "@/stores/spotlights"
const { items } = storeToRefs(useSpotlightStore())
const itemsWithIds = computed(() => items.value?.filter(i => Boolean(i.id)))
</script>

<style scoped lang="scss">
    nav {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        padding-top: .5rem;
        a {
            color: white;
            &:hover {
                text-decoration: none;
            }
        }
    }
</style>
