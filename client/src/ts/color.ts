// https://stackoverflow.com/a/54014428
// input: h in [0,360] and s,v in [0,1] 
// output: hexstring
function hsl2rgb(h: number, s: number, l: number): string {
  const a = s * Math.min(l, 1 - l);
  const f = (n, k = (n + h / 30) % 12) => l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
  const rgb = (n) => Math.floor(f(n) * 255);
  const r = rgb(0);
  const g = rgb(8);
  const b = rgb(4);
  return `${(16777216 | b | (g << 8) | (r << 16)).toString(16).slice(1)}`;
}

/** Random safe colors: not too light */
export function randomColor(): string {
  // all hues
  const hue = Math.floor(Math.random() * 360)
  // saturation between 0.25 and 0.75
  const saturation = Math.random() * 0.5 + 0.25
  // lightness between 0.25 and 0.75
  const lightness = Math.random() * 0.45 + 0.2
  return hsl2rgb(hue, saturation, lightness)
}
