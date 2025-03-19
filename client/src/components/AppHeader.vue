<template>
    <header role="banner" :style="headerStyle">
        <div class="logo">
            <RouterLink to="/" :style="'position: relative'">
                <img src="/teniers_krantlezer.jpg" alt="courantenlogo"
                    style="position: absolute; z-index: -1; max-height: 72px; left: -1rem;" />
                <img src="/woordpeiler-logo.svg" alt="woordpeilerlogo" style="filter: opacity(0.8) brightness(100)" />
            </RouterLink>
            <div class="logo-text">
                <h2>
                    <a href="https://ivdnt.org/" target="_blank" tabindex="-1" rel="noopener noreferrer">
                        /&nbsp;instituut&nbsp;voor&nbsp;de&nbsp;Nederlandse&nbsp;taal&nbsp;/
                    </a>
                </h2>
                <h1>
                    <RouterLink to="/">
                        courantenpeiler
                    </RouterLink>
                </h1>
            </div>
        </div>



        <nav>
            <!-- regular links -->
            <template v-if="$internal">
                <RouterLink to="/trends">trends</RouterLink>
            </template>
            <RouterLink to="/grafiek">grafiek</RouterLink>
            <RouterLink to="/help">help</RouterLink>
            <RouterLink to="/over">over</RouterLink>
            <a href="http://svotmc10.ivdnt.loc/corpus-frontend/Couranten2024/search" target="_blank">couranten</a>

            <!-- hamburger menu -->
            <Button text severity="secondary" type="button" icon="pi pi-bars" @click="(event) => { menu.toggle(event) }"
                aria-haspopup="true" aria-controls="overlayMenu" id="hamburger" title="Menu" />
            <Menu ref="menu" id="overlayMenu" :model="menuItems" :popup="true" />
        </nav>

    </header>
    <footer v-if="isHomePage">
        <h2>woordtrends in de 17<sup>e</sup> eeuw</h2>
        <InputGroup>
            <InputText v-model.trim="word" placeholder="zoeken" @keyup.enter="search" />
            <Button severity="secondary" @click="search">
                <span class="pi pi-search"></span>
            </Button>
        </InputGroup>
    </footer>
</template>

<script setup lang="ts">
// Libraries
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
// PrimeVue
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import InputGroup from 'primevue/inputgroup';
import Menu from 'primevue/menu';
// Util
import { toTimestamp } from '@/ts/date';
import { isInternal } from '@/ts/internal';

// Fields
const word = ref();
const route = useRoute();
const router = useRouter();
const menu = ref();

// Computed
const isHomePage = computed(() => route.path == "/");
const headerStyle = computed(() => isHomePage.value ? { boxShadow: 'none' } : {});
const menuItems = computed(() => {
    let items = [
        {
            label: 'grafiek',
            icon: 'pi pi-chart-line',
            command: () => {
                router.push('/grafiek');
            }
        },
        {
            label: 'help',
            icon: 'pi pi-question',
            command: () => {
                router.push('/help');
            }
        },
        {
            label: 'over',
            icon: 'pi pi-info',
            command: () => {
                router.push('/over');
            }
        },
        {
            label: 'chn',
            icon: 'pi pi-database',
            url: 'https://ivdnt.org/corpora-lexica/corpus-hedendaags-nederlands/',
            target: '_blank'
        }
    ]

    if (isInternal()) {
        items.unshift({
            label: 'trends',
            icon: 'pi pi-sort-amount-up',
            command: () => {
                router.push('/trends');
            }
        },);
    }

    return items;
});

// Methods
function search() {
    router.push({ path: '/grafiek', query: { w: word.value, start: toTimestamp(new Date('1618-01-01')) } });
}
</script>


<style scoped lang="scss">
header {
    font-family: Schoolboek;
    min-height: 80px;
    border-bottom: 9px solid #E8503D;
    display: flex;
    justify-content: space-between;
    background-color: white;
    box-shadow: 0px 4px 5px 1px #ccc;
    z-index: 1;

    a {
        color: inherit;
        text-decoration: none;
    }

    .logo {
        display: flex;
        justify-content: space-between;
        align-items: center;

        img {
            min-width: 72px;
            margin: 0 1rem;
        }
    }

    .logo-text {
        align-self: flex-start;

        h1 {
            font-weight: 400;
            font-size: 2rem;
        }

        h2 {
            font-weight: 400;
            font-size: 0.9rem;
            margin-top: 0.2rem;
            margin-bottom: -0.2rem;
        }
    }

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-right: 1rem;
        gap: 1rem;

        a {
            font-size: 1.1rem;

            &:hover {
                text-decoration: underline;
            }
        }

        :deep(button#hamburger) span {
            font-size: 1.5rem;
        }
    }
}

#hamburger {
    display: none;
}

footer {
    background-color: #E8503D;
    width: 100%;
    padding-bottom: 1rem;
    display: flex;
    justify-content: start;
    align-items: center;
    box-shadow: 0px 4px 5px 1px #ccc;
    flex-direction: column;

    h2 {
        font-family: Schoolboek;
        font-weight: 400;
        font-size: 1.5rem;
        color: white;
        padding: 5px 0 14px 0;
    }

    :deep(.p-inputgroup) {
        width: 90%;
        height: 42px;
        max-width: 400px;

        .p-inputtext {
            font-size: 1.1rem;
            border: 0;
        }

        .p-button {
            border: 0;
            padding: 0 1.8rem;
            background-color: #ddd;

            &:hover,
            &:active {
                background-color: #ccc;
            }

            span {
                font-size: 1.2rem;
            }
        }
    }
}
</style>