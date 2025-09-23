<template>
    <fieldset>
        <label for="pos">Woordsoort</label>
        <div>
            <InputGroup>
                <InputGroupAddon>
                    <HelpButton>
                        <p>
                            De woordsoorten komen uit de
                            <a target="_blank" href="https://ivdnt.org/wp-content/uploads/2024/11/TDNV2_combi.pdf"
                                >Tagset Diachroon Nederlands (TDN)</a
                            >
                        </p>
                    </HelpButton>
                </InputGroupAddon>
                <select id="pos" placeholder="Woordsoort" v-model="selectedPos">
                    <option :value="undefined" disabled selected hidden class="default">Woordsoort</option>
                    <option v-for="option in options" :key="option.value" :value="option.value" class="option">
                        {{ option.label }}
                    </option>
                </select>
                <span class="pi pi-chevron-down"></span>
            </InputGroup>
        </div>
    </fieldset>
    <div class="pos-list" v-if="posList.length > 0">
        <Chip v-for="p in posList" :label="format(p)" :key="p" removable>
            <template #removeicon>
                <span class="pi pi-times" @click="remove(p)"></span>
            </template>
        </Chip>
    </div>
</template>

<script setup lang="ts">
import { usePosses } from "@/stores/fetch/posses"

const pos = defineModel<string>()
const posList = computed<string[]>({
    get() {
        if (!pos.value) return []
        return pos.value.split(" ")
    },
    set(newValue: string[]) {
        pos.value = newValue.join(" ")
    },
})

const { options } = storeToRefs(usePosses())
const selectedPos = ref<string>()
watch(selectedPos, (newValue) => {
    if (newValue) {
        posList.value = [...posList.value, newValue] // need to set array ref for computed set()
        nextTick(() => (selectedPos.value = undefined))
    }
})

function remove(p) {
    const copy = [...posList.value]
    copy.splice(copy.indexOf(p), 1)
    posList.value = copy // need to set array ref for computed set()
}
function format(p) {
    const selectLabel = options.value?.find((i) => i.value == p)
    return selectLabel?.label ?? ""
}
</script>

<style scoped lang="scss">
.p-inputgroup {
    position: relative;
    .pi {
        color: #94a3b8;
        position: absolute;
        right: 12px;
        top: 15px;
        pointer-events: none;
    }
    select {
        appearance: none;
        cursor: pointer;
        width: 170px;
        background-image: none;
        background-color: white;
        border: 1px solid #cbd5e1;
        color: #64748b;
        padding: 0 0.65rem;
        option {
            border-radius: 0;
        }
    }
}

.pos-list {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: stretch;
    padding-top: 0.5rem;
    .p-chip {
        background-color: white;
        padding: 0;
        gap: 0.15rem;
        display: flex;
        border-radius: 0;
        border: 1px solid #cbd5e1;
        font-size: 0.9rem;

        :deep(.p-chip-label) {
            padding: 0.35rem;
            flex: 1 1 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        span {
            border-left: 1px solid #cbd5e1;
            cursor: pointer;
            text-align: center;
            height: 100%;
            width: 30px;
            align-content: center;
            &:hover,
            &:focus {
                background-color: #eee;
            }
        }
    }
}
</style>
