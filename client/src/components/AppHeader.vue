<template>
    <header role="banner">
        <div class="logo">
            <a href="/">
                <img src="/corpustrends-logo.svg" alt="logo" />
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
header {
    font-family: Schoolboek;
    height: 100px;
    border-bottom: 0.4rem solid #4488ee;
    display: flex;
    justify-content: space-between;
    background-color: white;
    box-shadow: 0px 4px 5px 1px #ccc;

    h1 {
        font-weight: 400;
        font-size: 2.5rem;
        margin-top: -0.5rem;
    }

    h2 {
        font-weight: 400;
        font-size: 1rem;
    }

    a {
        color: inherit;
        text-decoration: none;
    }

    .logo {
        display: flex;
        justify-content: space-between;
        align-items: center;

        img {
            min-width: 100px;
            margin: 0 0.5rem;
        }
    }

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;

        a {
            margin: 0 1rem;
            font-size: 1.2rem;

            &:hover {
                text-decoration: underline;
            }
        }
    }
}
</style>
