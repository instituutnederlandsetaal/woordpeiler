<template>
    <main>
        <aside>
            <SearchItem />
            <SearchSettings />
        </aside>
        <GraphWrapper />
    </main>
</template>

<style scoped lang="scss">
@media screen and (max-width: 1024px) {
    :deep(.search-settings) {
        flex: 4;
    }
}
@media screen and (max-width: 768px) {
    :deep(.search-settings) {
        flex: auto;
    }
}
</style>
