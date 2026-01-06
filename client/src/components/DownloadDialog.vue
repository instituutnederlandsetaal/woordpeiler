<template>
    <Dialog modal v-model:visible="visible" header="Downloaden">
        <section>
            <h3>Grafiek</h3>
            <p>Download de grafiek</p>
            <Button severity="secondary">
                Downloaden
                <span class="pi pi-download" title="Downloaden"></span>
            </Button>
        </section>

        <section>
            <h3>Tabelgegevens</h3>
            <p>Download een csv-bestand.</p>
            <Button severity="secondary">
                Downloaden
                <span class="pi pi-download" title="Downloaden"></span>
            </Button>
        </section>

        <section>
            <h3>Huisstijlblokje</h3>
            <p>Download een stylistisch blokje zoals op de voorpagina.</p>
            <Button severity="secondary" @click="downloadHuisstijl">
                Downloaden
                <span class="pi pi-download" title="Downloaden"></span>
            </Button>
            <fieldset>
                <label for="color">Kleur</label>
                <ColorPicker id="color" />
            </fieldset>
            <fieldset>
                <label for="size">Grootte</label>
                <Select id="size" :options />
            </fieldset>
        </section>
    </Dialog>
</template>

<script setup lang="ts">
import { saveAs } from "file-saver"

const visible = defineModel<boolean>()
const options: string[] = ["1920×1080 (16:9)", "960×720 (4:3)"]

function downloadHuisstijl() {
    fetch("http://localhost:8000/huisstijl-svg?w=corona&start=2019-01-01&c=FF77CC&i=1m").then((res) => {
        console.log(res)
        res.blob().then((b) => saveAs(b, "corona.svg"))
    })
}
</script>

<style scoped lang="scss"></style>
