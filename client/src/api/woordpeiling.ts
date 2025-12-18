import type { Woordpeiling } from "@/types/spotlight"

export function getWoordpeiling(): Promise<Woordpeiling> {
    return window.fetch("assets/config/woordpeiling.json").then((res) => res.json())
}
