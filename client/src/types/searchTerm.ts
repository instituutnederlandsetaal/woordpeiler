import { invalidNgramText } from "@/types/search"

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

export function equalTerm(a: SearchTerm, b: SearchTerm): boolean {
    return a.wordform == b.wordform && a.pos == b.pos && a.lemma == b.lemma
}

export function invalidTerm(term: SearchTerm): boolean {
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
