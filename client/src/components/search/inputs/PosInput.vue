<template>
    <fieldset>
        <label for="pos">Woordsoort</label>
        <div>
            <InputGroup>
                <InputGroupAddon>
                    <HelpButton>
                        <p>De woordsoort deelt woorden in naar betekenis en gebruik.</p>
                        <DataTable
                            :value="[
                                { word: 'blauw', pos: 'bijvoeglijk naamwoord' },
                                { word: 'altijd', pos: 'bijwoord' },
                                { word: 'Europa', pos: 'eigennaam' },
                                { word: 'de', pos: 'lidwoord' },
                                { word: 'twee', pos: 'telwoord' },
                                { word: 'ja', pos: 'tussenwerpsel' },
                                { word: 'en', pos: 'voegwoord' },
                                { word: 'wij', pos: 'voornaamwoord' },
                                { word: 'met', pos: 'voorzetsel' },
                                { word: 'lopen', pos: 'werkwoord' },
                                { word: 'huis', pos: 'zelfstandig naamwoord' },
                            ]"
                            size="small"
                            style="max-width: fit-content"
                        >
                            <Column field="word" header="Woord"></Column>
                            <Column field="pos" header="Woordsoort"></Column>
                        </DataTable>
                    </HelpButton>
                </InputGroupAddon>
                <Select
                    id="pos"
                    :options
                    showClear
                    v-model="pos"
                    optionLabel="label"
                    optionValue="value"
                    placeholder="Woordsoort"
                    :loading="!options"
                />
            </InputGroup>
        </div>
    </fieldset>
</template>

<script setup lang="ts">
import { usePosses } from "@/stores/fetch/posses"
const { options } = storeToRefs(usePosses())
const pos = defineModel<string>({
    set: (value) => {
        if (value) return value
        return undefined
    },
})
</script>

<style scoped lang="scss">
.p-inputgroup .p-select {
    align-items: center;
    :deep(span:not(.p-placeholder)) {
        font-size: 0.9rem;
    }
}
</style>
