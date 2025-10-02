<template>
    <main>
        <div class="panel">
            <Tabs value="0" class="text-panel">
                <TabList>
                    <Tab value="0">Algemeen</Tab>
                    <Tab value="1">Basiszoeken</Tab>
                </TabList>
                <TabPanels>
                    <TabPanel value="0" tabindex="-1">
                        <GeneralHelp />
                    </TabPanel>
                    <TabPanel value="1" tabindex="-1">
                        <BasicHelp />
                    </TabPanel>
                </TabPanels>
            </Tabs>
        </div>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core"
import BasicHelp from "@/views/help/BasicHelp.vue"
import GeneralHelp from "@/views/help/GeneralHelp.vue"

let scrolledToBottom = false

useEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        if (!scrolledToBottom) {
            scrolledToBottom = true
            window.plausible("scrolled_to_bottom")
        }
    }
})
</script>

<style scoped lang="scss">
:deep(figure) {
    display: flex;
    align-items: center;
    flex-direction: column;
    padding: 1rem 0;
    img {
        border: 1px solid #ddd;
        padding: 0.5rem;
        display: flex;
        max-width: 800px;
    }
    figcaption {
        margin-top: 0.5rem;
    }
}

main {
    height: fit-content;
    flex: 1;

    .panel {
        display: flex;
        justify-content: center;
        border: 1px solid #e2e8f0;
        background: white;
        width: 100%;
        flex: 1;
        min-height: 100%;

        .text-panel {
            max-width: 1000px;
        }
    }
}
</style>
