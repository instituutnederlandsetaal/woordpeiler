<template>
    <section>
        <h2>Algemeen</h2>
        <p>
            Met <i>Woordpeiler</i> kunt u bekijken hoe vaak woorden door de tijd heen voorkomen in teksten uit
            Nederlandstalige kranten. Zoek op een woord en <i>Woordpeiler</i> visualiseert de frequentie ervan door de
            jaren heen in een grafiek, vanaf 2000 tot nu.
        </p>
        <p>
            Het woord
            <RouterLink to="/grafiek?w=vapen">vapen</RouterLink>
            kwam bijvoorbeeld in 2014 voor het eerst een enkele keer voor, maar vanaf 2022 is er een duidelijke stijging
            te zien van het gebruik van dit woord in de kranten. De woorden
            <RouterLink to="/grafiek?w=mondkapje,mondmasker">mondkapje en mondmasker</RouterLink>
            kenden een opvallende piek van 2020 tot 2022 en voor het woord
            <RouterLink to="/grafiek?w=televisie">televisie</RouterLink>
            is een dalende trend zichtbaar. Deze trends weerspiegelen niet alleen maatschappelijke en technologische
            ontwikkelingen (vapen, televisie), maar ook veranderingen in woordkeuze (zie bijvoorbeeld
            <RouterLink to="/grafiek?w=videogame,videospel">videogame en videospel</RouterLink>) of de verschillen
            tussen de taalvariëteiten (mondkapje/mondmasker).
        </p>
        <p>
            De grafiek staat standaard ingesteld op de default-instellingen van de zoekfunctie. Er zijn verschillende
            aanpassingen mogelijk, die beschreven staan bij het tabje
            <i>Basiszoeken</i>.
        </p>
        <p>
            Hieronder staan de visualisaties van de bovengenoemde voorbeelden als voorbeeld. Op de x-as is de tijd
            weergegeven in jaren, maanden of dagen. De y-as toont de woordfrequentie.
        </p>

        <figure>
            <Image preview>
                <template #image>
                    <img src="@/assets/img/vapen.png" alt="Grafiek van de woordfrequentie van vapen" />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/vapen.png"
                        alt="Grafiek van de woordfrequentie van vapen"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Grafiek van de woordfrequentie van vapen.</figcaption>
        </figure>

        <figure>
            <Image preview>
                <template #image>
                    <img
                        src="@/assets/img/mondkapje.png"
                        alt="Grafiek van de woordfrequentie van mondkapje en mondmasker"
                    />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/mondkapje.png"
                        alt="Grafiek van de woordfrequentie van mondkapje en mondmasker"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Grafiek van de woordfrequentie van mondkapje en mondmasker.</figcaption>
        </figure>

        <figure>
            <Image preview>
                <template #image>
                    <img
                        src="@/assets/img/videospel.png"
                        alt="Grafiek van de woordfrequentie van videospel en videogame"
                    />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/videospel.png"
                        alt="Grafiek van de woordfrequentie van videospel en videogame"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Grafiek van de woordfrequentie van videospel en videogame.</figcaption>
        </figure>

        <figure>
            <Image preview>
                <template #image>
                    <img src="@/assets/img/televisie.png" alt="Grafiek van de woordfrequentie van televisie" />
                </template>
                <template #original="slotProps">
                    <img
                        src="@/assets/img/televisie.png"
                        alt="Grafiek van de woordfrequentie van televisie"
                        :style="slotProps.style"
                        @click="slotProps.onClick"
                    />
                </template>
            </Image>
            <figcaption>Grafiek van de woordfrequentie van televisie.</figcaption>
        </figure>
    </section>
</template>
