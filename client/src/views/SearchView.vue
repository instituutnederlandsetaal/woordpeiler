<template>
    <main>
        <aside>
            <WordListView />
            <SearchSettings />
        </aside>
        <D3Graph />
    </main>
</template>

<script setup lang="ts">
// Components
import D3Graph from "@/components/graph/GraphWrapper.vue"
import WordListView from "@/components/WordList.vue"
import SearchSettings from "@/components/SearchSettings.vue"
</script>
