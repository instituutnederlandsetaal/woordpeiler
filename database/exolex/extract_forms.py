import sys
import gzip
import json

# https://kaikki.org/dictionary/rawdata.html
if __name__ == "__main__":
    path = sys.argv[1]

    unique_keys = set()

    i = 0

    with gzip.open(path, mode="rt", encoding="utf-8") as file:
        for line in file:
            data = json.loads(line)
            # print all keys
            # add all keys to the set
            unique_keys.update(data.keys())
            i += 1
            if i > 10000000:
                break

    sorted_keys = sorted(unique_keys)
    print(sorted_keys)
    # ['abbreviations', 'anagrams', 'antonyms', 'categories', 'derived', 'descendants', 'etymology_texts', 'forms', 'holonyms', 'homophones', 'hypernyms', 'hyphenation', 'hyponyms', 'lang', 'lang_code', 'metonyms', 'notes', 'paronyms', 'pos', 'pos_title', 'proverbs', 'redirect', 'related', 'senses', 'sounds', 'synonyms', 'tags', 'title', 'translations', 'word']
