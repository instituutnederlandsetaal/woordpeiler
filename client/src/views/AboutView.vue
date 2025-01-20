<template>
    <main>
        <Panel class="textPanel">
            <section>
                <h2>Over de applicatie</h2>
                <p>
                    <i>Woordpeiler</i> is gemaakt door het Instituut voor de Nederlandse Taal (INT). De website maakt
                    gebruik
                    van de data uit het Corpus Hedendaags Nederlands (CHN), en voor onderzoekers is er vanuit
                    <i>Woordpeiler</i> een directe koppeling naar het CHN om gedetailleerde (meta)data te kunnen
                    bekijken.
                </p>
            </section>
            <section>
                <h2>Bronmateriaal</h2>
                <p>
                    De gegevens in <i>Woordpeiler</i> komen uit het krantenmateriaal van het
                    <a href="https://ivdnt.org/corpora-lexica/corpus-hedendaags-nederlands/">
                        Corpus Hedendaags Nederlands
                    </a>.
                </p>
                <h3>Samenstelling</h3>
                <ul>
                    <li>
                        <i>Antilliaans-Nederlands:</i>
                        Antilliaans Dagblad, Amigoe, Aruba.nu, Bonaire.nu, Curacao.nu, Paradise FM 103.1.
                    </li>
                    <li>
                        <i>Belgisch-Nederlands:</i>
                        De Morgen, De Standaard, Gazet van Antwerpen, Het Belang van Limburg, Het Laatste
                        Nieuws,
                        Het Nieuwsblad, Wablieft, WAI-NOT Krant.
                    </li>
                    <li>
                        <i>Nederlands-Nederlands:</i>
                        ANP, Algemeen Dagblad, Dordrechts Dagblad, Elsevier, De Groene Amsterdammer, de
                        Volkskrant,
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
            <div class="logos">
                <a href="https://www.ivdnt.org">
                    <img src="@/assets/ivdNt-logo-3regels.svg" alt="Logo Instituut voor de Nederlandse taal"
                        title="Instituut voor de Nederlandse taal" />
                </a>
            </div>
        </Panel>
    </main>
</template>

<script setup lang="ts">
import Panel from 'primevue/panel';
</script>

<style scoped lang="scss">
.logos {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 3rem;

    a {
        display: block;
        width: 100%;
        max-width: 200px;

        img {
            width: 100%;
        }
    }
}
</style>