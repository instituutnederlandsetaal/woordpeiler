<template>
  <AppHeader />
  <RouterView />

  <Dialog :visible @update:visible="visible = false; errors = []" modal header="Foutmelding" class="errorDialog">
    <ul>
      <li v-for="error in errors" :key="errors.indexOf(error)">{{ error }}</li>
    </ul>
    <p>Blijft dit probleem zich voordoen? </p>
    <p>Neem contact op met <a href="mailto:servicedesk@ivdnt.org">servicedesk@ivdnt.org</a>.</p>
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

<style scoped lang="scss">
ul {
  margin-bottom: 0.5rem;
}
</style>