<template>
    <Panel class="helpPanel">
        <h2>Basiszoeken</h2>
        <p>Klik op het plusje om een nieuwe zoekopdracht toe te voegen.</p>
    </Panel>
</template>

<script setup lang="ts">
import Panel from 'primevue/panel';
</script>

<style scoped lang="scss">
.helpPanel {
    margin: 1rem;
    width: 100%;

    :deep(.p-panel-header) {
        padding: 0.3rem !important;
    }
}
</style>