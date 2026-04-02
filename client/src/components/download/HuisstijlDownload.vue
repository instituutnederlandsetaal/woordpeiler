<template>
    <Panel class="panel" header="Huisstijlblokje">
        <figure>
            <div v-if="svg" v-html="svg"></div>
            <Skeleton height="150px" v-else />
            <Button severity="secondary" @click="download">
                Downloaden
                <span class="pi pi-download" title="Downloaden"></span>
            </Button>
        </figure>
        <form>
            <fieldset>
                <IftaLabel class="flex-1">
                    <Select inputId="word" :options="words" v-model="word" :disabled="words.length == 1" />
                    <label for="word">Woord</label>
                </IftaLabel>
                <IftaLabel>
                    <InputText inputId="color" v-keyfilter.hex maxLength="6" v-model="color" id="color" />
                    <label for="color">Kleur</label>
                </IftaLabel>
                <ColorPicker v-model="color" />
            </fieldset>
            <fieldset>
                <IftaLabel class="flex-1">
                    <Select
                        fluid
                        inputId="size"
                        :options="sizes"
                        v-model="size"
                        optionLabel="label"
                        optionValue="value"
                    />
                    <label for="size">Grootte</label>
                </IftaLabel>
                <IftaLabel>
                    <Select inputId="format" :options="formats" v-model="format" />
                    <label for="format">Type</label>
                </IftaLabel>
            </fieldset>
            <IntervalInput v-model="interval" />
        </form>
    </Panel>
</template>

<script setup lang="ts">
import { saveAs } from "file-saver"
import { useSearchResults } from "@/stores/search/searchResults"
import { searchToString } from "@/types/search"
import * as API from "@/api/svg"
import type { SvgRequest } from "@/api/svg"
import { computedAsync } from "@vueuse/core"
import type { SelectLabel } from "@/types/ui"

const sizes: SelectLabel[] = [
    { label: "960×720 (4:3)", value: { x: 960, y: 720 } },
    { label: "1920×1080 (16:9)", value: { x: 1920, y: 1080 } },
    { label: "1080×1350 (4:5) (Instagram)", value: { x: 1080, y: 1350 } },
    { label: "1080×1440 (3:4) (Instagram)", value: { x: 1080, y: 1440 } },
]

const formats: string[] = ["png", "svg"]
const color = ref<string>("fff064")
const size = ref<string>(sizes[0]?.value)
const format = ref<string>(formats[0])
const { searchResults } = storeToRefs(useSearchResults())
const words = computed(() => searchResults.value.map((i) => searchToString(i.searchItem)))
const word = ref<string>()
const interval = ref<string>()

const svg = computedAsync(async () => {
    if (!word.value) return
    const req: SvgRequest = {
        w: word.value,
        c: color.value,
        f: "svg",
        start: "2000-01-01",
        x: size.value.x,
        y: size.value.y,
        i: interval.value,
    }
    return await (await API.getHuisstijlSvg(req)).data.text()
})

watch(words, () => (word.value = words.value[0]), { immediate: true })

function download() {
    const req: SvgRequest = {
        w: word.value,
        c: color.value,
        f: format.value,
        start: "2000-01-01",
        x: size.value.x,
        y: size.value.y,
        i: interval.value,
    }
    API.getHuisstijlSvg(req).then((res) => {
        saveAs(new Blob([res.data]), `${word.value}.${format.value}`)
    })
}
</script>

<style scoped lang="scss">
:deep(.p-panel-content) {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    figure {
        align-self: center;
        width: 250px;
        display: flex;
        flex-direction: column;
    }
    form {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        fieldset {
            display: flex;
            gap: 0.5rem;
            justify-content: space-between;
            justify-items: center;
            align-items: center;
            align-content: center;
            --p-colorpicker-preview-width: 2rem;
            --p-colorpicker-preview-height: 2rem;
            .p-iftalabel {
                display: flex !important;
            }
            .flex-1 {
                flex: 1;
                > div {
                    flex: 1;
                }
            }
            #color {
                width: 100px;
            }
        }
    }
}
</style>
