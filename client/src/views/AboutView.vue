<template>
    <main>
        <Panel class="helpPanel">
            <section>
                <h2>Over Woordpeiler</h2>
                <p>

                </p>
                <h3>Bronmateriaal</h3>
                <p>
                    De gegevens in <i>Woordpeiler</i> komen uit het krantenmateriaal van het
                    <a href="https://ivdnt.org/corpora-lexica/corpus-hedendaags-nederlands/">
                        Corpus Hedendaags Nederlands
                    </a>.
                </p>
                <h4>Samenstelling</h4>
                <ul>
                    <li>
                        <i>Antilliaans-Nederlands:</i>
                        Antilliaans Dagblad, Amigoe, Aruba.nu, Bonaire.nu, Curacao.nu, Paradise FM 103.1.
                    </li>
                    <li>
                        <i>Belgisch-Nederlands:</i>
                        De Morgen, De Standaard, Gazet van Antwerpen, Het Belang van Limburg, Het Laatste Nieuws,
                        Het Nieuwsblad, Wablieft, WAI-NOT Krant.
                    </li>
                    <li>
                        <i>Nederlands-Nederlands:</i>
                        ANP, Algemeen Dagblad, Dordrechts Dagblad, Elsevier, De Groene Amsterdammer, de Volkskrant,
                        HP/De Tijd, Het Parool, Meppeler Courant, NRC, Start!-krant, Trouw, Vrij Nederland.
                    </li>
                    <li>
                        <i>Surinaams-Nederlands:</i>
                        De Ware Tijd, Starnieuws.
                    </li>
                </ul>
                <p>
                </p>
            </section>
        </Panel>
    </main>
</template>

<script setup lang="ts">
import Panel from 'primevue/panel';
import ColorPicker from 'primevue/colorpicker';

const canShare = navigator.share != undefined;
</script>

<style scoped lang="scss">
.helpPanel {
    width: 100%;
    min-height: 100%;
    height: fit-content;

    :deep(.p-panel-header) {
        padding: 0.7rem;
    }

    :deep(.p-panel-content) {
        padding: 0 2rem;
        padding-bottom: 3rem !important;
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