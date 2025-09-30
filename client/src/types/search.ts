import { config } from "@/main"

export interface SearchItem {
    terms?: SearchTerm[]
    source?: string
    language?: string
    color?: string
    visible?: boolean
    loading?: boolean
    uuid: string
}

export interface SearchTerm {
    wordform?: string
    pos?: string
    lemma?: string
}

export function termToString(t: SearchTerm): string | undefined {
    return (
        Object.values({ w: t.wordform, l: t.lemma ? `‘${t.lemma}’` : undefined, p: t.pos })
            .filter(Boolean)
            .join("–") || undefined
    )
}

export function searchToString(item: SearchItem): string | undefined {
    const terms = item.terms?.map(termToString).filter(Boolean).join(" ") || undefined
    const source = item.language ?? item.source ?? undefined
    const sourceStr = source ? `(${source})` : undefined
    return [terms, sourceStr].filter(Boolean).join(" ") || undefined
}

export function equalSearchItem(a: SearchItem, b: SearchItem): boolean {
    if (a.terms?.length != b.terms?.length) {
        return false
    }
    for (let i = 0; i < a.terms?.length; i++) {
        if (!equalSearchTerm(a.terms[i], b.terms[i])) {
            return false
        }
    }
    return a.source == b.source && a.language == b.language
}

export function equalSearchTerm(a: SearchTerm, b: SearchTerm): boolean {
    return a.wordform == b.wordform && a.pos == b.pos && a.lemma == b.lemma
}

export function invalidNgram(item: SearchItem): boolean {
    return (item.terms?.length ?? 0) > config.search.ngram
}

export function invalidText(text: string, ngram: number): boolean {
    const dummyItem: SearchItem = { terms: [{ wordform: text }] }
    return invalidNgramText(text, ngram) || invalidStarWildcard(dummyItem) || invalidQuestionWildcard(dummyItem)
}

export function invalidNgramText(text: string, ngram: number): boolean {
    // trim leading, trailing, and multiple spaces inside
    const trimmedText = text?.replace(/\s+/g, " ").trim() ?? ""
    const num_words = trimmedText.split(" ").length ?? 0
    if (num_words > ngram) {
        return true // invalid
    }
    return false // valid
}

export function invalidStarWildcard(item: SearchItem): boolean {
    return invalidWildcard(item, "*", 4)
}

export function invalidQuestionWildcard(item: SearchItem): boolean {
    return invalidWildcard(item, "?", 2)
}

function invalidWildcardsUsage(item: SearchItem): boolean {
    return invalidStarWildcard(item) || invalidQuestionWildcard(item)
}

function invalidWildcard(item: SearchItem, wildcard: string, minChars: number): boolean {
    for (const term of item.terms ?? []) {
        for (const text of [term.lemma, term.wordform]) {
            const split = text?.trim()?.split(" ") ?? []
            for (const word of split) {
                // regex only allowed with at least minChars characters
                if (word.includes(wildcard)) {
                    if (word.replaceAll(wildcard, "").length < minChars) {
                        return true // invalid
                    }
                }
            }
        }
    }
    return false // valid
}

export function invalidSearchItem(item: SearchItem): boolean {
    // Either lemma or wordform must be truthy.
    if (!item.terms) {
        // todo not just pos
        return true // invalid
    }
    // Truthy, but check ngram and wildcards too.
    if (invalidNgram(item) || invalidWildcardsUsage(item)) {
        return true // invalid
    }
    return false // valid
}

export function invalidSearchTerm(term: SearchTerm): boolean {
    // Either lemma or wordform must be truthy.
    if (!term.wordform && !term.lemma) {
        return true // invalid
    }
    // Truthy, but check ngram and wildcards too.
    if (invalidNgramText(term.wordform, 1) || invalidNgramText(term.lemma, 1)) {
        return true // invalid
    }
    return false // valid
}
