// https://stackoverflow.com/a/54014428
// input: h in [0,360] and s,v in [0,1]

import type { SearchItem } from "@/types/search"

// output: hexstring
function hsl2rgb(h: number, s: number, l: number): string {
    const a = s * Math.min(l, 1 - l)
    const f = (n, k = (n + h / 30) % 12) => l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
    const rgb = (n) => Math.floor(f(n) * 255)
    const r = rgb(0)
    const g = rgb(8)
    const b = rgb(4)
    return `${(16777216 | b | (g << 8) | (r << 16)).toString(16).slice(1)}`
}

let lastUsedIndex = -1
export function randomColor(): string {
    return colorScheme[++lastUsedIndex % colorScheme.length]
}

export function randomUnusedColor(items: SearchItem[]): string {
    const usedColors = new Set(items.map((d) => d.color?.replace("#", "").toUpperCase()))
    const available = colorScheme.filter((d) => !usedColors.has(d))
    if (available.length === 0) {
        return randomColor() // tough luck
    }
    return available[0]
}

export const colorScheme = [
    "000000",
    "DD0000",
    "00DD00",
    "0000DD",
    "DDDD00",
    "DD00DD",
    "00DDDD",
    "888888",
    "880000",
    "000088",
    "008800",
    "DD8800",
    "DD0088",
    "88DD88",
    "8800DD",
    "0088DD",
]
