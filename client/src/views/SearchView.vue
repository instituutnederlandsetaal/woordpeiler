<template>
    <main>
        <aside>
            <WordListView />
            <SearchSettings />
        </aside>
        <GraphWrapper />
    </main>
</template>

<script setup lang="ts">
// Components
import GraphWrapper from "@/components/graph/GraphWrapper.vue"
import WordListView from "@/components/WordList.vue"
import SearchSettings from "@/components/SearchSettings.vue"
</script>
