<template>
    <p v-if="trends.length == 0">Loading...</p>
    <ul>
        <li v-for="trend in trends" :key="trend"><a target="_blank" :href="`/?wordform=${trend}`">{{ trend }}</a></li>
    </ul>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const trends = ref([])

onMounted(() => {
    console.log('mounted')
})

onMounted(() => {
    const url = `http://localhost:8000/trends`
    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            data.forEach((d) => {
                trends.value.push(d.wordform)
            })
        })
})
</script>