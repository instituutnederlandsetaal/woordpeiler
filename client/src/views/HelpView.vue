<template>
    <main>
        <Panel class="textPanel">
            <section>
                <h2>Basiszoeken</h2>
                <ul>
                    <li>
                        <b>Woord:</b>
                        het woord waarop u zoekt is niet hoofdletter- of accentgevoelig: met
                        <RouterLink to="/grafiek?w=tiktok">tiktok</RouterLink> vindt u ook TikTok
                        en met <RouterLink to="/grafiek?w=belgie">belgie</RouterLink> vindt u ook België.
                    </li>
                    <li>
                        <b>Taalvariëteit:</b>
                        standaard staat de grafiek ingesteld op alle taalvariëteiten van het Nederlands die in het
                        krantenmateriaal vertegenwoordigd zijn. Wilt u alleen de data uit een specifieke taalvariëteit
                        zien? Kies de variëteit in dit menu. Door op het kruisje te klikken verwijdert u de selectie
                        weer. Vergeet niet opnieuw op "Zoeken" te klikken.
                    </li>
                    <li>
                        <b>Kleur:</b>
                        de kleur van de zoekterm in de grafiek is aan te passen door op het gekleurde blokje
                        <ColorPicker /> te klikken. Dit is vooral nuttig als u op verschillende termen tegelijk zoekt.
                    </li>
                    <li>
                        <b>Zichtbaarheid:</b>
                        door op het oogje <span class="pi pi-eye"></span> te klikken kunt u een zoekterm in de grafiek
                        tonen (default) of verbergen. Dit is vooral nuttig als u op verschillende termen tegelijk zoekt.
                    </li>
                    <li>
                        <b>Verwijderen:</b>
                        klik op het prullenbakje <span class="pi pi-trash"></span> om een zoekterm uit de lijst te
                        verwijderen.
                    </li>
                    <li>
                        <b>In- en uitklappen:</b>
                        klik op <span class="pi pi-minus"></span> om een zoekterm in de lijst in- of uit te klappen.
                    </li>
                    <li>
                        <b>Toevoegen:</b>
                        klik op de
                        <Button class="dummyNewWord" severity="secondary" title="Zoekterm toevoegen" outlined>
                            <span class="pi pi-plus"></span>
                        </Button>
                        om een nieuwe zoekterm toe te voegen aan de grafiek.
                    </li>
                </ul>
            </section>

            <section>
                <h2>Zoekinstellingen</h2>
                <p>
                    Linksonder in de grafiekview vindt u de zoekinstellingen. Klik op <span
                        class="pi pi-chevron-down"></span> om de instellingen te openen.
                </p>
                <ul>
                    <li>
                        <b>Splits automatisch op taalvariëteit:</b>
                        vink deze optie aan om de zoekterm in de grafiek automatisch op alle taalvariëteiten te
                        splitsen. De variëteiten krijgen verschillende kleuren die terug te vinden zijn in de legenda
                        linksboven in de grafiek.
                    </li>
                    <li>
                        <b>Frequentie:</b>
                        kies tussen <i>absolute frequentie</i> (het totaal aantal voorkomens) of
                        <i>relatieve frequentie</i> (het aantal voorkomens per 1 miljoen woorden).
                    </li>
                    <li>
                        <b>Periode:</b>
                        kies een zoekperiode in de tijd.
                        De knop <span class="pi pi-refresh"></span> zet de periode terug op de standaardinstelling
                        <i>2000 &ndash; nu</i>.
                    </li>
                    <li>
                        <b>Interval:</b>
                        dit is het interval waarover de frequentie wordt berekend.
                        Bijvoorbeeld: <i>per 1 jaar</i>, <i>per 2 maanden</i> of <i>per 3 weken</i>.
                        Standaard staat deze instelling op per 3 maanden.
                    </li>

                </ul>
            </section>

            <section>
                <h2>Grafiek</h2>
                <p>In de grafiek kunt u op een bepaalde periode inzoomen, en u kunt de grafiek als afbeelding
                    downloaden.</p>
                <ul>
                    <li>
                        <b>Inzoomen:</b>
                        zoom in op een periode door met de cursor over de grafiek te slepen (houd de linkermuisknop
                        ingedrukt). Er verschijnt een grijs selectievak en zodra u de muisknop loslaat zoomt u in op dit
                        deel van de grafiek.
                    </li>
                    <li>
                        <b>Uitzoomen:</b>
                        dubbelklik op de grafiek om weer uit te zoomen.
                    </li>
                    <li>
                        <b>Downloaden:</b>
                        klik op de downloadknop <span class="pi pi-download"></span> om de grafiek als afbeelding te
                        downloaden.
                    </li>
                    <li v-if="canShare">
                        <b>Delen:</b>
                        klik op de deelknop <span class="pi pi-share-alt"></span> om de grafiek te delen via de
                        interface van
                        Android /
                        iOS.
                    </li>
                </ul>
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
</style>