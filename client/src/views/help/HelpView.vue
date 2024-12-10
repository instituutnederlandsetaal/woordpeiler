<template>
    <Panel class="helpPanel">
        <section>
            <h2>Basiszoeken</h2>
            <ul>
                <li>
                    <b>Toevoegen:</b>
                    klik op
                    <Button class="dummyNewWord" severity="secondary" title="Zoekterm toevoegen" outlined>
                        <span class="pi pi-plus"></span>
                    </Button>
                    om een nieuwe zoekopdracht toe te voegen.
                </li>
                <li>
                    <b>Woord:</b>
                    het woord waarop u wilt zoeken.
                    Niet hoofdletter- of accentgevoelig:
                    met <i>belgie</i> vindt u ook <i>België</i>.
                </li>
                <li>
                    <b>Taalvariëteit:</b>
                    kies uit de lijst een taalvariëteit van het Nederlands waarin u het woord wilt zoeken.
                </li>
                <li>
                    <b>In- en uitklappen:</b>
                    klik op <span class="pi pi-plus"></span> of <span class="pi pi-minus"></span> om een zoekterm in de
                    lijst te in- of uit te klappen.
                </li>
                <li>
                    <b>Verwijderen:</b>
                    klik op <span class="pi pi-trash"></span> om een zoekterm uit de lijst te verwijderen.
                </li>
                <li>
                    <b>Zichtbaarheid:</b>
                    klik op <span class="pi pi-eye"></span> of <span class="pi pi-eye-slash"></span> om een zoekterm in
                    de
                    grafiek te verbergen of te tonen.
                </li>
                <li>
                    <b>Kleur:</b>
                    klik op
                    <ColorPicker /> om de kleur van een zoekterm in de grafiek aan te passen.
                </li>
            </ul>
        </section>
        <section>
            <h2>Grafiek</h2>
            <ul>
                <li>
                    <b>Inzoomen:</b>
                    zoom in op een periode door over de grafiek te slepen.
                </li>
                <li>
                    <b>Uitzoomen:</b>
                    dubbelklik op de grafiek om uit te zoomen.
                </li>
                <li>
                    <b>Downloaden:</b>
                    klik op <span class="pi pi-download"></span> om de grafiek als afbeelding te downloaden.
                </li>
                <li v-if="canShare">
                    <b>Delen:</b>
                    klik op <span class="pi pi-share-alt"></span> om de grafiek te delen via de interface van Android /
                    iOS.
                </li>
            </ul>
        </section>

        <section>
            <h2>Zoekinstellingen</h2>
            <ul>
                <li>
                    <b>Frequentie:</b>
                    kies tussen <i>absolute frequentie</i> (het totaal aantal voorkomens) of
                    <i>relatieve frequentie</i> (het aantal voorkomens per 1 miljoen woorden).
                </li>
                <li>
                    <b>Periode:</b>
                    kies een zoekperiode in de tijd.
                    De knop <span class="pi pi-refresh"></span> zet de periode terug op <i>2000 &ndash; nu</i>.
                </li>
                <li>
                    <b>Tijdsinterval:</b>
                    de interval waarover de frequentie wordt berekend.
                    Bijvoorbeeld: <i>per 1 jaar</i>, <i>per 2 maanden</i> of <i>per 3 weken</i>.
                </li>
            </ul>
        </section>

                    </li>
                </ul>
            </section>

    </Panel>
</template>

<script setup lang="ts">
import Panel from 'primevue/panel';
import ColorPicker from 'primevue/colorpicker';

const canShare = navigator.share != undefined;
</script>

<style scoped lang="scss">
.helpPanel {
    width: 100%;

    :deep(.p-panel-header) {
        padding: 0.7rem !important;
    }

    :deep(.p-panel-content) {
        padding: 0 2rem !important;
    }

    section {
        margin-bottom: 1rem;
    }
}

.dummySearchSettings {
    max-width: 500px;
}

span.pi,
.p-colorpicker {
    padding: 0 0.2rem;
}

.dummyNewWord {
    border: 2px dashed #ccc;
    background: #eee;
    width: 60px;

    span {
        font-size: 0.8rem;
    }
}

ul {
    list-style-type: none;
    padding-left: 0;
}

li {
    margin-bottom: 0.4rem;

    b {
        margin-right: 0.25rem;
    }
}
</style>