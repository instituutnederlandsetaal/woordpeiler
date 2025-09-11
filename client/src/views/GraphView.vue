<template>
    <main>
        <aside>
            <SearchItem />
            <SearchSettings />
        </aside>
        <GraphWrapper />
    </main>
</template>

<script setup lang="ts">
import { config } from "@/main"

document.title = `${config.app.name} - Grafiek`
</script>

<style scoped lang="scss">
@media screen and (max-width: 1024px) {
    :deep(.search-settings) {
        flex: 4;
    }
}
@media screen and (max-width: 768px) {
    :deep(.search-settings) {
        flex: auto;
    }
}
</style>
