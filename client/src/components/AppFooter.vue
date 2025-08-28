<template>
    <footer>
        <p>© 2025 Instituut voor de Nederlandse Taal, alle rechten voorbehouden</p>
        <div>
            <a href="https://ivdnt.org/privacyverklaring">privacyverklaring</a>
            <a href="https://ivdnt.org/gebruiksvoorwaarden/">gebruiksvoorwaarden</a>
        </div>
    </footer>
</template>

<style scoped lang="scss">
footer {
    border-top: #d9d9d9 solid 1px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    justify-content: center;
    align-items: center;
    text-align: center;
    background-color: #f3f3f3;
    padding: 3rem 1rem;
    font-size: 0.9rem;
    p {
        max-width: 1000px;
    }
    div {
        display: flex;
        gap: 1rem;
    }
}
</style>
