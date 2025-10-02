<template>
    <section>
        <h2>Basiszoeken</h2>

        <ul>
            <li>
                <h3>Woord:</h3>
                het woord waarop u zoekt is niet hoofdletter- of accentgevoelig: met
                <RouterLink to="/grafiek?w=tiktok">tiktok</RouterLink>
                vindt u ook TikTok en met
                <RouterLink to="/grafiek?w=belgie">belgie</RouterLink>
                vindt u ook België.
            </li>
            <li>
                <h3>Taalvariëteit:</h3>
                standaard staat de grafiek ingesteld op alle taalvariëteiten van het Nederlands die in het
                krantenmateriaal vertegenwoordigd zijn. Wilt u alleen de data uit een specifieke taalvariëteit zien?
                Kies de variëteit in dit menu. Door op het kruisje te klikken verwijdert u de selectie weer. Vergeet
                niet opnieuw op "Zoeken" te klikken.
            </li>
            <li>
                <h3>Kleur:</h3>
                de kleur van de zoekterm in de grafiek is aan te passen door op het gekleurde blokje
                <ColorPicker /> te klikken. Dit is vooral nuttig als u op verschillende termen tegelijk zoekt.
            </li>
            <li>
                <h3>Zichtbaarheid:</h3>
                door op het oogje
                <span class="pi pi-eye"></span> te klikken kunt u een zoekterm in de grafiek tonen (default) of
                verbergen. Dit is vooral nuttig als u op verschillende termen tegelijk zoekt.
            </li>
            <li>
                <h3>Verwijderen:</h3>
                klik op het prullenbakje
                <span class="pi pi-trash"></span> om een zoekterm uit de lijst te verwijderen.
            </li>
            <li>
                <h3>In- en uitklappen:</h3>
                klik op
                <span class="pi pi-chevron-up"></span> of <span class="pi pi-chevron-down"></span> om een zoekterm in de
                lijst in- of uit te klappen.
            </li>
            <li>
                <h3>Tooltip woord:</h3>
                klik op
                <span class="pi pi-question"></span> om uitleg te krijgen over verfijning van de zoekopdracht met
                jokertekens. In de woordpeiler zijn er twee jokertekens: het vraagteken (<b>?</b>) en de asterisk
                (<b>*</b>):
                <ul>
                    <li>
                        Het vraagteken staat voor een willekeurig karakter. Met <dfn>z?n</dfn> vindt u bijvoorbeeld
                        <em>zon</em>, <em>zin</em> en <em>zen</em> en met <dfn>?z?n</dfn> vindt u bijvoorbeeld
                        <em>azen</em> en <em>ozo</em>. U kunt meerdere vraagtekens combineren, zolang er maar ten minste
                        twee andere tekens gebruikt worden;
                    </li>
                    <li>
                        De asterisk staat voor geen, één of meer willekeurige karakters. Met <dfn>*gebaar</dfn> vindt u
                        bijvoorbeeld <em>gebaar</em>, <em>handgebaar</em> en <em>vredesgebaar</em> en met
                        <dfn>*baar*</dfn> vindt u bijvoorbeeld <em>baar</em>, <em>aaibaar</em>, <em>baarmoeder</em> en
                        <em>bakkebaard</em>. U kunt meerdere asterisken combineren, zolang er maar ten minste vier
                        andere tekens gebruikt worden;
                    </li>
                    <li>
                        Het is ook mogelijk om beide jokertekens te combineren. Met <dfn>*he?d</dfn> vindt u
                        bijvoorbeeld <em>held</em>, <em>superheld</em> en <em>aaibaarheid</em>.
                    </li>
                </ul>
            </li>
            <li>
                <h3>Toevoegen:</h3>
                klik op de
                <span class="dummyNewWord pi pi-plus"></span>
                om een nieuwe zoekterm toe te voegen aan de grafiek.
            </li>
        </ul>

        <figure>
            <Image preview>
                <template #image>
                    <img src="@/assets/img/zoekterm.png" alt="Voorbeeldzoekterm" />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/zoekterm.png"
                        alt="Voorbeeldzoekterm"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Een voorbeeldzoekterm.</figcaption>
        </figure>
    </section>

    <section>
        <h2>Zoekinstellingen</h2>
        <p>
            Linksonder in de grafiekview vindt u de zoekinstellingen. Klik op
            <span class="pi pi-chevron-up"></span> om de instellingen te openen.
        </p>
        <ul>
            <li>
                <h3>Splits automatisch op taalvariëteit:</h3>
                vink deze optie aan om de zoekterm in de grafiek automatisch op alle taalvariëteiten te splitsen. De
                variëteiten krijgen verschillende kleuren die terug te vinden zijn in de legenda linksboven in de
                grafiek.
            </li>
            <li>
                <h3>Frequentie:</h3>
                kies tussen <i>absolute frequentie</i> (het totaal aantal voorkomens) of
                <i>relatieve frequentie</i> (het aantal voorkomens per 1 miljoen woorden).
            </li>
            <li>
                <h3>Periode:</h3>
                kies een zoekperiode in de tijd. De knop
                <span class="pi pi-refresh"></span> zet de periode terug op de standaardinstelling
                <i>2000 &ndash; nu</i>.
            </li>
            <li>
                <h3>Interval:</h3>
                dit is het interval waarover de frequentie wordt berekend. Bijvoorbeeld:
                <i>per 1 jaar</i>, <i>per 2 maanden</i> of <i>per 3 weken</i>. Standaard staat deze instelling op per 3
                maanden.
            </li>
        </ul>

        <figure>
            <Image preview>
                <template #image>
                    <img src="@/assets/img/zoekinstellingen.png" alt="Zoekinstellingen" />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/zoekinstellingen.png"
                        alt="Zoekinstellingen"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>
                De zoekinstellingen (linksonderin) met <i>splits automatisch op taalvariëteit</i> aangezet.
            </figcaption>
        </figure>
    </section>

    <section>
        <h2>Grafiek</h2>
        <p>In de grafiek kunt u op een bepaalde periode inzoomen, en u kunt de grafiek als afbeelding downloaden.</p>
        <ul>
            <li>
                <h3>Inzoomen:</h3>
                zoom in op een periode door met de cursor over de grafiek te slepen (houd de linkermuisknop ingedrukt).
                Er verschijnt een grijs selectievak en zodra u de muisknop loslaat, zoomt u in op dit deel van de
                grafiek.
            </li>
            <li>
                <h3>Uitzoomen:</h3>
                dubbelklik op de grafiek om weer uit te zoomen of klik op de uitzoomknop
                <span class="pi pi-search-minus"></span>.
            </li>
            <li>
                <h3>Downloaden:</h3>
                klik op de downloadknop
                <span class="pi pi-download"></span> om de grafiek als afbeelding te downloaden.
            </li>
            <li v-if="canShare">
                <h3>Delen:</h3>
                klik op de deelknop
                <span class="pi pi-share-alt"></span> om de grafiek te delen via de interface van Android / iOS.
            </li>
            <li>
                <h3>Punten in de curve:</h3>
                als u met uw muis over een punt in de curve gaat, verschijnt een tekstvakje met een samenvatting van de
                corpusgegevens waarvoor het punt staat: het woord, de datum en de relatieve of absolute frequentie.
                Onderzoekers kunnen ook doorklikken om de gegevens voor dat punt in het CHN te bekijken.
            </li>
            <li>
                <h3>Legenda:</h3>
                voor elke curve in de grafiek wordt de kleur, het woord en eventueel de taalvariëteit aangegeven. Door
                op een woord in de legenda te klikken, kunnen onderzoekers in het CHN de onderliggende gegevens voor de
                hele curve bekijken. Let wel, bij een tijdsindeling in weken, of met intervallen niet gelijk aan 1,
                worden de gegevens in het CHN met een kleinere datumgranulariteit weergegeven.
            </li>
        </ul>

        <figure>
            <Image preview>
                <template #image>
                    <img src="@/assets/img/slepen.png" alt="Zoomen met grijs selectievak" />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/slepen.png"
                        alt="Zoomen met grijs selectievak"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Zoomen met grijs selectievak.</figcaption>
        </figure>
    </section>
</template>

<script setup lang="ts">
const canShare = navigator.share != undefined
</script>

<style scoped lang="scss">
span.pi,
.p-colorpicker {
    padding: 0 0.2rem;
}

.dummyNewWord {
    width: 60px;
    border: 2px dashed #ccc !important;
    background: #eee;
    height: 30px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
</style>
