<template>
    <section>
        <h2>Geavanceerd zoeken</h2>
        <p>
            Bij geavanceerd zoeken kunt u uw zoekopdracht uitbreiden met woordsoort en lemma. Het lemma is de
            woordenboekvorm van een woord. De woordsoort deelt woorden in naar betekenis en gebruik.
        </p>

        <ul>
            <li>
                <h3>Verschil lemma en woord:</h3>
                bij woord is het enkel mogelijk om een specifieke woordvorm te zoeken. Zoeken naar
                <em>fatbike</em> geeft enkel informatie over die vorm. Zoekt u echter bij lemma op <em>fatbike</em>, dan
                wordt ook op alle vormen gezocht die bij het lemma horen, in dit geval het meervoud <em>fatbikes</em>.
                <ul>
                    <li>
                        <h3>Tooltip lemma:</h3>
                        klik op <span class="pi pi-question"></span> om uitleg te krijgen over lemma in relatie tot
                        woord en woordsoort. Elk lemma heeft ook een woordsoort, bijvoorbeeld bijvoeglijk naamwoord voor
                        <em>blauw</em> en zelfstandig naamwoord voor <em>huis</em>.
                    </li>
                </ul>
            </li>
            <li>
                <h3>Zoeken met en zonder woordsoort:</h3>
                bij woordsoort is het mogelijk om de zoekopdracht nader te verfijnen met een woordsoort. Dit kan nuttig
                zijn om te zoeken naar een woord met enkel die woordsoort. Door in lemma of woord te zoeken op
                <em>eten</em>
                vindt u bijvoorbeeld resultaten voor het zelfstandig naamwoord "(het) eten" naast (een vorm van) het
                werkwoord "eten". Door als woordsoort zelfstandig naamwoord te selecteren kunt u zoekresultaten van het
                werkwoord uitsluiten.
                <ul>
                    <li>
                        <h3>Tooltip woordsoort:</h3>
                        klik op <span class="pi pi-question"></span> om uitleg te krijgen over de verschillende
                        woordsoorten. Sommige woorden (of lemmata) behoren tot meerdere woordsoorten. U kunt kiezen uit:
                        bijvoeglijk naamwoord, bijwoord, eigennaam, lidwoord, telwoord, tussenwerpsel, voegwoord,
                        voornaamwoord, voorzetsel, werkwoord, zelfstandig naamwoord.
                    </li>
                </ul>
            </li>
        </ul>

        <figure>
            <Image preview>
                <template #image>
                    <img src="@/assets/img/geavanceerd.png" alt="Geavanceerde zoekterm" />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/geavanceerd.png"
                        alt="Geavanceerde zoekterm"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Een geavanceerde zoekterm.</figcaption>
        </figure>
    </section>
</template>

<style scoped lang="scss">
h3 {
    display: inline;
    font-size: 1rem;
    font-weight: bold;
    font-family: inherit;
    margin-right: 0.3rem;
}
</style>
