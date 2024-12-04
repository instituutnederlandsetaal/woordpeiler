<template>
    <header role="banner">
        <div class="logo">
            <a href="/">
                <img src="@/assets/corpustrends-logo.svg" alt="logo" />
            </a>
            <div class="logo-text">
                <a href="https://ivdnt.org/" target="_blank" tabindex="-1" rel="noopener noreferrer">
                    /&nbsp;instituut&nbsp;voor&nbsp;de&nbsp;Nederlandse&nbsp;taal&nbsp;/
                </a>
                <!-- <h2>/instituut voor de Nederlandse taal/</h2> -->
                <a href="/">
                    <h1>corpustrends</h1>
                </a>
            </div>
        </div>
        <nav>
            <template v-if="$internal">
                <a href="/">grafiek</a>
                <a href="/trends">trends</a>
            </template>
            <a href="/uitleg">uitleg</a>
        </nav>
    </header>
</template>

<style scoped lang="scss">
img {
    width: 100px;
    margin: 0 0.5rem;
}
</style>
