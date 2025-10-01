<template>
    <Button type="button" icon="pi pi-question" severity="secondary" variant="text" @click="toggle" />
    <Popover ref="popup">
        <slot></slot>
    </Popover>
</template>

<script setup lang="ts">
import Popover from "primevue/popover"

const popup = useTemplateRef<InstanceType<typeof Popover>>("popup")

function toggle(e: Event) {
    popup.value?.toggle(e)
}
</script>

<style lang="scss">
ul {
    padding-left: 1rem;
    margin: 0.5rem 0;
    li {
        padding: 0.25rem 0;
        dfn {
            font-family: monospace;
            font-style: normal;
            font-weight: bold;
            border: 1px solid #ccc;
            padding: 0.1rem 0.4rem;
        }
    }
}
</style>
