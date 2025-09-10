<template>
    <header :style="headerStyle">
        <div class="logo">
            <div class="logo-img">
                <RouterLink to="/">
                    <img :src="$config.theme.logo" alt="logo" />
                </RouterLink>
            </div>
            <div class="logo-text">
                <h2>
                    <a href="https://ivdnt.org/" target="_blank" rel="noopener noreferrer">
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
                aria-haspopup="true"
                aria-controls="hamburger-menu"
                id="hamburger"
                title="Menu"
                @click="toggleMenu"
            />
            <Menu ref="menu" id="hamburger-menu" :model="menuItems" :popup="true" />
        </nav>
    </header>
</template>

<script setup lang="ts">
// Util
import { config } from "@/main"
import { isInternal } from "@/ts/internal"

// Fields
const route = useRoute()
const router = useRouter()
const menu = ref()

// Computed
const isHomePage = computed(() => route.path === "/")
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
            label: config.corpus.name.toLowerCase(),
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

// methods
function toggleMenu(event: MouseEvent) {
    menu.value.toggle(event)
}
</script>

<style scoped lang="scss">
@use "@/assets/primevue.scss" as *;

header {
    z-index: 1;
    height: 70px;
    border-bottom: 5px solid $theme;
    display: flex;
    justify-content: space-between;
    background-color: white;
    box-shadow: 0px 4px 5px 1px #ccc;

    a {
        font-family: "Schoolboek", "Helvetica Neue", Helvetica, Arial, sans-serif;
        color: inherit;
        text-decoration: none;
    }

    .logo {
        display: flex;
        line-height: normal;
        gap: 0.5rem;

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
        justify-content: end;
        align-content: center;
        align-items: center;
        flex-wrap: wrap;
        padding-right: 36px;
        gap: 32px;
        row-gap: 0;

        a {
            font-size: 16px;

            &:hover {
                text-decoration: underline;
            }
        }

        :deep(button#hamburger) {
            width: 65px;
            span {
                font-size: 1.5rem;
            }
        }
    }
}

#hamburger {
    display: none;
}
</style>
