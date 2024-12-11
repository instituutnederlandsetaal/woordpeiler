<template>
    <main>
        <aside>
            <WordListView />
            <SearchOptions :languageSplit="$internal" />
        </aside>

        <D3Graph />
    </main>
</template>

<script setup lang="ts">
// Components
import D3Graph from "@/components/graph/GraphWrapper.vue"
import WordListView from "@/components/WordList.vue"
import SearchOptions from "@/components/SearchSettings.vue"
</script>
