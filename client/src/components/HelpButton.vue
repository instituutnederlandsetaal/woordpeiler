<template>
    <Button type="button" icon="pi pi-question" variant="text" severity="secondary" @click="toggle" />
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
