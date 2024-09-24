<template>
    <HeaderView />
    <main>
        <SearchView />
        <GraphView />
    </main>
</template>

<script setup lang="ts">
import infixRpnEval from "infix-rpn-eval"

import HeaderView from "@/views/HeaderView.vue"
import GraphView from "@/views/GraphView.vue"
import SearchView from "@/views/SearchView.vue"
</script>
