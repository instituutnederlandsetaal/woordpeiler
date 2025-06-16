<template>
    <header role="banner" :style="headerStyle">
        <div class="logo">
            <div class="logo-img">
                <RouterLink to="/">
                    <img :src="$config.theme.logo" alt="logo" />
                </RouterLink>
            </div>
            <div class="logo-text">
                <h2>
                    <a href="https://ivdnt.org/" target="_blank" tabindex="-1" rel="noopener noreferrer">
                        /&nbsp;instituut&nbsp;voor&nbsp;de&nbsp;Nederlandse&nbsp;taal&nbsp;/
                    </a>
                </h2>
                <h1>
                    <RouterLink to="/">{{ $config.app.name.toLowerCase() }}</RouterLink>
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
            <a :href="$config.corpus.url" target="_blank">{{ $config.corpus.name.toLowerCase() }}</a>

            <!-- hamburger menu -->
            <Button
                text
                severity="secondary"
                type="button"
                icon="pi pi-bars"
                @click="
                    (event) => {
                        menu.toggle(event)
                    }
                "
                aria-haspopup="true"
                aria-controls="overlayMenu"
                id="hamburger"
                title="Menu"
            />
            <Menu ref="menu" id="overlayMenu" :model="menuItems" :popup="true" />
        </nav>
    </header>
    <footer v-if="isHomePage">
        <h2>{{ $config.app.slogan }}</h2>
        <InputGroup>
            <InputText v-model.trim="word" placeholder="zoeken" @keyup.enter="search" />
            <Button severity="secondary" @click="search" title="Zoeken">
                <span class="pi pi-search"></span>
            </Button>
        </InputGroup>
    </footer>
</template>

<script setup lang="ts">
// Util
import { toTimestamp } from "@/ts/date"
import { isInternal } from "@/ts/internal"

// Fields
const word = ref()
const route = useRoute()
const router = useRouter()
const menu = ref()

// Computed
const isHomePage = computed(() => route.path == "/")
const headerStyle = computed(() => (isHomePage.value ? { boxShadow: "none" } : {}))
const menuItems = computed(() => {
    const items = [
        {
            label: "grafiek",
            icon: "pi pi-chart-line",
            command: () => {
                router.push("/grafiek")
            },
        },
        {
            label: "help",
            icon: "pi pi-question",
            command: () => {
                router.push("/help")
            },
        },
        {
            label: "over",
            icon: "pi pi-info",
            command: () => {
                router.push("/over")
            },
        },
        {
            label: "chn",
            icon: "pi pi-database",
            url: "https://ivdnt.org/corpora-lexica/corpus-hedendaags-nederlands/",
            target: "_blank",
        },
    ]

    if (isInternal()) {
        items.unshift({
            label: "trends",
            icon: "pi pi-sort-amount-up",
            command: () => {
                router.push("/trends")
            },
        })
    }

    return items
})

// Methods
function search() {
    router.push({ path: "/grafiek", query: { w: word.value, start: toTimestamp(new Date("1618-01-01")) } })
}
</script>

<style scoped lang="scss">
@use "@/assets/primevue.scss" as *;

header {
    font-family: Schoolboek;
    height: 70px;
    border-bottom: 5px solid $theme;
    display: flex;
    justify-content: space-between;
    background-color: white;
    z-index: 1;

    a {
        color: inherit;
        text-decoration: none;
    }

    .logo {
        display: flex;
        line-height: normal;
        gap: 1rem;

        .logo-img img {
            height: 65px;
        }

        .logo-text {
            padding: 5px 0;

            display: flex;
            flex-direction: column;

            h1 {
                font-weight: normal;
                font-size: 1.7rem;
            }

            h2 {
                font-weight: normal;
                font-size: 0.8rem;
            }
        }
    }

    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-right: 36px;
        gap: 32px;

        a {
            font-size: 16px;

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
    background-color: $theme;
    width: 100%;
    padding-bottom: 1rem;
    display: flex;
    justify-content: start;
    align-items: center;
    box-shadow: 0px 4px 5px 1px #ccc;
    flex-direction: column;

    h2 {
        font-family: Schoolboek;
        font-weight: normal;
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
