<template>
    <main>
        <Panel class="text-panel">
            <section>
                <h2>Over de applicatie</h2>
                <p>
                    <i>Woordpeiler</i> is gemaakt door het Instituut voor de Nederlandse Taal (INT). De API wordt
                    verzorgd door FastAPI in Python. De frequentiegegevens zijn verkregen met de BlackLab FrequencyTool
                    en zitten in een PostgreSQL-database met de TimescaleDB-plugin. De webpagina is gemaakt met Vue 3 en
                    de grafieken met D3.js.
                </p>
            </section>
            <section>
                <h2>Over de Woordpeiler</h2>
                <p>
                    De website maakt gebruik van de data uit het Corpus Hedendaags Nederlands (CHN), en voor
                    onderzoekers is er vanuit <i>Woordpeiler</i> een directe koppeling naar het CHN om gedetailleerde
                    (meta)data te kunnen bekijken.
                </p>
                <section>
                    <h3>Bronmateriaal</h3>
                    <p>
                        De gegevens in <i>Woordpeiler</i> komen uit het krantenmateriaal van het
                        <a href="https://ivdnt.org/corpora-lexica/corpus-hedendaags-nederlands/"
                            >Corpus Hedendaags Nederlands</a
                        >. De teksten in het corpus worden automatisch verwerkt en taalkundig geanalyseerd. De
                        woordfrequenties kunnen daarom licht beïnvloed zijn door fouten in de woordsplitsing of
                        krantenartikelen die hernomen worden in kranten van dezelfde uitgeversgroep.
                    </p>
                </section>
            </section>
            <section>
                <h2>Credits</h2>
                <p>
                    Wanneer u verwijst naar de <i>Woordpeiler</i>, gebruik dan de volgende referentie (Gelieve de datum
                    van raadpleging toe te voegen aan de referentie, aangezien het corpus maandelijks geüpdatet wordt):
                </p>
                <section>
                    <h3>Voor Woordpeiler:</h3>
                    <p>
                        Software beschikbaar op:
                        <a href="https://github.com/instituutnederlandsetaal/woordpeiler">
                            https://github.com/instituutnederlandsetaal/woordpeiler
                        </a>
                    </p>
                    <cite>
                        Woordpeiler (Versie 2.0.0) (Oktober 2025) [Online Service]. Toegankelijk gemaakt door het
                        Instituut voor de Nederlandse Taal
                        <a href="https://hdl.handle.net/10032/tm-a3-a3">https://hdl.handle.net/10032/tm-a3-a3</a>.
                        Geraadpleegd op [datum].
                    </cite>
                </section>
                <section>
                    <h3>Voor BlackLab:</h3>
                    <p>
                        Software beschikbaar op:
                        <a href="https://github.com/instituutnederlandsetaal/blacklab">
                            https://github.com/instituutnederlandsetaal/blacklab
                        </a>
                    </p>
                    <cite>
                        Does, Jesse de, Jan Niestadt en Katrien Depuydt (2017), Creating research environments with
                        BlackLab. In: Jan Odijk and Arjan van Hessen (eds.) CLARIN in the Low Countries, pp. 151-165.
                        London: Ubiquity Press. DOI:
                        <a href="https://doi.org/10.5334/bbi">https://doi.org/10.5334/bbi</a>
                    </cite>
                </section>
                <section>
                    <h3>Voor BlackLab Frontend</h3>
                    <p>
                        Software beschikbaar op:
                        <a href="https://github.com/instituutnederlandsetaal/blacklab-frontend"
                            >https://github.com/instituutnederlandsetaal/blacklab-frontend</a
                        >
                    </p>
                </section>
            </section>
            <section>
                <h2>Suggesties of vragen</h2>
                <p>
                    Voor suggesties of vragen kunt u een mail sturen naar
                    <a href="mailto:servicedesk@ivdnt.org">servicedesk@ivdnt.org</a>.
                </p>
            </section>
        </Panel>
    </main>
    <AppFooter />
</template>

<script setup lang="ts">
import { useEventListener } from "@vueuse/core"

let scrolledToBottom = false

useEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        if (!scrolledToBottom) {
            scrolledToBottom = true
            window.plausible("scrolled_to_bottom")
        }
    }
})
</script>

<style scoped lang="scss">
main {
    min-height: initial;
}
</style>
