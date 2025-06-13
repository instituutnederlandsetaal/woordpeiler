export function isInternal(): boolean {
    // url parameter to force external mode
    if (window.location.search.includes("extern")) {
        return false
    } else {
        // else check if we are on a local environment
        return ["localhost", ".ivdnt.loc"].some((url) => window.location.hostname.includes(url))
    }
}
