// https://stackoverflow.com/a/54014428
// input: h in [0,360] and s,v in [0,1]
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

/** Random safe colors: not too light */
export function randomColor(): string {
    return colorScheme[Math.floor(Math.random() * colorScheme.length)]
}

// https://sronpersonalpages.nl/~pault/#fig:scheme_rainbow_discrete
export const colorScheme = [
    "D1BBD7", // no. 3
    "AE76A3", // no. 6
    "882E72", // no. 9
    "1965B0", // no. 10
    "5289C7", // no. 12
    "7BAFDE", // no. 14
    "4EB265", // no. 15
    "90C987", // no. 16
    "CAE0AB", // no. 17
    "F7F056", // no. 18
    "F6C141", // no. 20
    "F1932D", // no. 22
    "E8601C", // no. 24
    "DC050C", // no. 26
    "000000", // custom
]
