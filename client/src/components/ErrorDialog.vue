<template>
    <Dialog modal :visible header="Foutmelding" :draggable="false" @update:visible="errors = []">
        <ul>
            <li v-for="error in errors" :key="error">
                {{ error }}
            </li>
        </ul>
        <p>Blijft dit probleem zich voordoen?</p>
        <p>Neem contact op met <a href="mailto:servicedesk@ivdnt.org">servicedesk@ivdnt.org</a>.</p>
    </Dialog>
</template>

<script setup lang="ts">
import { useErrors } from "@/stores/errors"
const { errors } = storeToRefs(useErrors())
const visible = ref<boolean>(false)

watch(
    errors,
    () => {
        visible.value = errors.value.length > 0
    },
    { deep: true },
)
</script>

<style scoped lang="scss">
ul {
    margin-bottom: 0.5rem;
}
</style>
