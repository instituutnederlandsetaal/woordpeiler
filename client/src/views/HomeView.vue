<template>
    <p class="event-banner">
        Meer leren over de functionaliteiten van Woordpeiler, over hoe je de grafieken interpreteert en op wat voor manieren je het kunt gebruiken? 
        Schrijf je in voor het <a href="https://ivdnt.org/evenement/webinar-woordpeiler/?utm_source=woordpeiler&utm_medium=referral&utm_campaign=banner">gratis webinar op 7 oktober</a>!
    </p>
    <main>
        <div class="wrapper">
            <SpotlightBlock v-for="spotlight in items" :key="spotlight.word" :spotlight />
        </div>
    </main>
</template>

<script setup lang="ts">
// Libraries
import { storeToRefs } from "pinia"
// Stores
import { useSpotlightStore } from "@/stores/SpotlightStore"
// Components
import SpotlightBlock from "@/components/spotlight/SpotlightBlock.vue"
import { onMounted } from "vue"

// Stores
const spotlightStore = useSpotlightStore()
const { items } = storeToRefs(spotlightStore)
const { fetchSpotlights } = spotlightStore

// Lifecycle
onMounted(() => {
    fetchSpotlights()
})

</script>

<style scoped lang="scss">
body {
    overflow: auto;
    height: fit-content;
}

.wrapper {
    display: flex;
    flex-wrap: wrap;
    align-content: start;
    justify-content: safe center;
    gap: 1rem;
    margin: 0 auto;
    padding-bottom: 1rem;
    height: fit-content;

    section {
        // height
        height: calc(250px + 10vw);
        max-height: 400px;
        // width
        width: 400px;
        flex-grow: 1;
        max-width: 500px;
        // Without this, boxes with long text will grow to max-width, even if the screen is smaller
        overflow: hidden;
    }
}

.event-banner {
    margin: 0 auto;
    padding: 1rem 2rem 0 2rem;
    max-width: 865px;
    text-align: center;
    font-size: 1.2rem;
    a {
        color: black;
        
        &:hover {
            text-decoration: none;
        }
    }
}

@media screen and (max-width: 600px) {
    .event-banner {
        font-size: 1rem;
    }
}
</style>
