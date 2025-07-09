<template>
    <footer class="footer">
        <p>
            De gegevens in <i>Woordpeiler</i> komen uit het krantenmateriaal van het
            <a href="https://ivdnt.org/corpora-lexica/corpus-hedendaags-nederlands/">Corpus Hedendaags Nederlands</a>.
            De teksten in het corpus worden automatisch verwerkt en taalkundig geanalyseerd. De woordfrequenties kunnen
            daarom licht beïnvloed zijn door fouten in de woordsplitsing of krantenartikelen die hernomen worden in
            kranten van dezelfde uitgeversgroep.
        </p>
        <p>© 2025 Instituut voor de Nederlandse Taal, alle rechten voorbehouden</p>
    </footer>
</template>

<style scoped lang="scss">
.footer {
    border-top: #d9d9d9 solid 1px;
    display: flex;
    flex-direction: column;
    gap: 2rem;
    justify-content: center;
    align-items: center;
    text-align: center;
    background-color: #f3f3f3;
    padding: 3rem 1rem;
    font-size: 0.9rem;
    p {
        max-width: 1000px;
    }
}
</style>
