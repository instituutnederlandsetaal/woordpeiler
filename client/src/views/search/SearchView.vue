<template>
    <div class="search">
        <WordListView />
        <SearchOptions :languageSplit="$internal" />
    </div>

    <D3Graph />
</template>

<script setup lang="ts">
// Components
import D3Graph from "@/components/graph/GraphWrapper.vue"
import WordListView from "@/components/WordList.vue"
import SearchOptions from "@/components/SearchSettings.vue"
</script>
