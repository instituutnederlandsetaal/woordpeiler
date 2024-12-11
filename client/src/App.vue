<template>
  <AppHeader />
  <RouterView />

  <Dialog :visible @update:visible="visible = false; errors = []" modal header="Error">
    <ul>
      <li v-for="error in errors" :key="errors.indexOf(error)">{{ error }}</li>
    </ul>
    <br />
    <p>Probeer het later opnieuw...</p>
  </Dialog>

</template>

<script setup lang="ts">
// Libraries
import { RouterView } from 'vue-router'
import { onMounted, ref, watch } from 'vue';
import { storeToRefs } from 'pinia';
// Stores
import { useErrorsStore } from './stores/ErrorsStore';
// Components
import AppHeader from '@/components/AppHeader.vue';
// primevue
import Dialog from "primevue/dialog"

// Stores
const errorStore = useErrorsStore()
const { errors } = storeToRefs(errorStore)

// Fields
const visible = ref(false);

// Lifecycle
watch(errors, () => {
  if (errors.value.length > 0) {
    visible.value = true;
  }
}, { deep: true });

onMounted(() => {
  errorStore.setupErrorHandler()
});
</script>
