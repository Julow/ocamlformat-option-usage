import requests
import json
import re
import itertools

ALL_OPTIONS = {
    "align-cases": ["true", "false"],
    "align-constructors-decl": ["true", "false"],
    "align-variants-decl": ["true", "false"],
    "assignment-operator": ["begin-line", "end-line"],
    "break-before-in": ["fit-or-vertical", "auto"],
    "break-cases": ["fit", "nested", "toplevel", "fit-or-vertical", "all"],
    "break-collection-expressions": ["wrap", "fit-or-vertical"],
    "break-infix": ["wrap", "fit-or-vertical"],
    "break-infix-before-func": ["true", "false"],
    "break-fun-decl": ["wrap", "fit-or-vertical", "smart"],
    "break-fun-sig": ["wrap", "fit-or-vertical", "smart"],
    "break-separators": ["before", "after", "after-and-docked"],
    "break-sequences": ["true", "false"],
    "break-string-literals": ["newlines", "never", "wrap", "newlines-and-wrap"],
    "break-struct": ["true", "false"],
    "cases-exp-indent": None,
    "cases-matching-exp-indent": ["normal", "compact"],
    "comment-check": ["true", "false"],
    "disable": ["true", "false"],
    "disambiguate-non-breaking-match": ["true", "false"],
    "doc-comments": ["before", "after"],
    "doc-comments-padding": None,
    "doc-comments-tag-only": ["fit", "default"],
    "escape-chars": ["decimal", "hexadecimal", "preserve"],
    "escape-strings": ["decimal", "hexadecimal", "preserve"],
    "exp-grouping": ["parens", "preserve"],
    "extension-indent": None,
    "extension-sugar": ["preserve", "always"],
    "field-space": ["tight", "loose", "tight-decl"],
    "function-indent": None,
    "function-indent-nested": ["always", "auto", "never"],
    "if-then-else": ["compact", "fit-or-vertical", "keyword-first", "k-r"],
    "indent-after-in": None,
    "indicate-multiline-delimiters": ["no", "space", "closing-on-separate-line"],
    "indicate-nested-or-patterns": ["space", "unsafe-no"],
    "infix-precedence": ["indent", "parens"],
    "leading-nested-match-parens": ["true", "false"],
    "let-and": ["compact", "sparse"],
    "let-binding-indent": None,
    "let-binding-spacing": ["compact", "sparse", "double-semicolon"],
    "let-module": ["compact", "sparse"],
    "let-open": ["preserve", "auto", "short", "long"],
    "margin": None,
    "match-indent": None,
    "match-indent-nested": ["always", "auto", "never"],
    "max-indent": ["none"],
    "max-iters": None,
    "module-item-spacing": ["compact", "preserve", "sparse"],
    "nested-match": ["wrap", "align"],
    "ocp-indent-compat": ["true", "false"],
    "parens-ite": ["true", "false"],
    "parens-tuple": ["always", "multi-line-only"],
    "parens-tuple-patterns": ["always", "multi-line-only"],
    "parse-docstrings": ["true", "false"],
    "quiet": ["true", "false"],
    "sequence-blank-line": ["compact", "preserve-one"],
    "sequence-style": ["before", "separator", "terminator"],
    "single-case": ["compact", "sparse"],
    "space-around-arrays": ["true", "false"],
    "space-around-lists": ["true", "false"],
    "space-around-records": ["true", "false"],
    "space-around-variants": ["true", "false"],
    "stritem-extension-indent": None,
    "type-decl": ["compact", "sparse"],
    "type-decl-indent": None,
    "wrap-comments": ["true", "false"],
    "wrap-fun-args": ["true", "false"],
    "profile": ["ocamlformat", "conventional", "compact", "sparse", "janestreet" ]
}

default_profile = { opt: (None if val is None else val[0]) for opt, val in ALL_OPTIONS.items() }

ALL_PROFILES = {
    "ocamlformat": default_profile,
    "conventional": { **default_profile,
        "break-cases": "fit",
        "break-infix-before-func": "false",
        "break-separators": "after-and-docked",
        "break-sequences": "true",
        "cases-matching-exp-indent": "normal",
        "field-space": "loose",
        "indicate-nested-or-patterns": "unsafe-no",
        "sequence-style": "terminator",
        "sequence-blank-line": "preserve-one",
        "space-around-arrays": "true",
        "space-around-lists": "true",
        "space-around-records": "true",
        "space-around-variants": "true" },
    "compact": { **default_profile,
        "break-before-in": "auto",
        "break-cases": "fit",
        "break-collection-expressions": "wrap",
        "break-infix": "wrap",
        "break-fun-decl": "wrap",
        "break-fun-sig": "wrap",
        "break-sequences": "false",
        "break-struct": "false",
        "doc-comments-tag-only": "fit",
        "exp-grouping": "parens",
        "field-space": "tight",
        "if-then-else": "compact",
        "indicate-nested-or-patterns": "space",
        "leading-nested-match-parens": "false",
        "let-and": "compact",
        "let-binding-spacing": "compact",
        "let-module": "compact",
        "module-item-spacing": "compact",
        "single-case": "compact",
        "space-around-arrays": "false",
        "space-around-lists": "false",
        "space-around-records": "false",
        "space-around-variants": "false",
        "type-decl": "compact",
        "wrap-fun-args": "true" },
    "sparse": { **default_profile,
        "break-before-in": "fit-or-vertical",
        "break-cases": "nested",
        "break-collection-expressions": "fit-or-vertical",
        "break-infix": "fit-or-vertical",
        "break-fun-decl": "smart",
        "break-fun-sig": "smart",
        "break-sequences": "true",
        "break-struct": "true",
        "field-space": "loose",
        "if-then-else": "keyword-first",
        "indicate-nested-or-patterns": "space",
        "leading-nested-match-parens": "true",
        "let-and": "sparse",
        "let-binding-spacing": "sparse",
        "let-module": "sparse",
        "module-item-spacing": "sparse",
        "single-case": "sparse",
        "sequence-blank-line": "preserve-one",
        "space-around-arrays": "true",
        "space-around-lists": "true",
        "space-around-records": "true",
        "space-around-variants": "true",
        "type-decl": "sparse",
        "wrap-fun-args": "false" },
    "janestreet": { **default_profile,
        "align-constructors-decl": "false",
        "align-cases": "false",
        "align-variants-decl": "false",
        "assignment-operator": "begin-line",
        "break-before-in": "fit-or-vertical",
        "break-cases": "fit-or-vertical",
        "break-infix": "fit-or-vertical",
        "break-infix-before-func": "true",
        "break-fun-decl": "fit-or-vertical",
        "break-fun-sig": "fit-or-vertical",
        "break-separators": "before",
        "break-sequences": "true",
        "break-string-literals": "wrap",
        "cases-exp-indent": None,
        "cases-matching-exp-indent": "normal",
        "comment-check": "true",
        "disable": "false",
        "disambiguate-non-breaking-match": "false",
        "doc-comments": "before",
        "doc-comments-padding": None,
        "doc-comments-tag-only": "fit",
        "escape-chars": "preserve",
        "escape-strings": "preserve",
        "exp-grouping": "parens",
        "extension-indent": None,
        "extension-sugar": "preserve",
        "field-space": "loose",
        "function-indent": None,
        "function-indent-nested": "never",
        "if-then-else": "keyword-first",
        "indent-after-in": None,
        "indicate-multiline-delimiters": "no",
        "indicate-nested-or-patterns": "unsafe-no",
        "infix-precedence": "parens",
        "leading-nested-match-parens": "true",
        "let-and": "sparse",
        "let-binding-indent": None,
        "let-binding-spacing": "double-semicolon",
        "let-module": "sparse",
        "let-open": "preserve",
        "margin": None,
        "match-indent": None,
        "match-indent-nested": "never",
        "max-indent": None,
        "max-iters": None,
        "module-item-spacing": "compact",
        "nested-match": "wrap",
        "ocp-indent-compat": "true",
        "parens-ite": "true",
        "parens-tuple": "multi-line-only",
        "parens-tuple-patterns": "multi-line-only",
        "parse-docstrings": "false",
        "sequence-blank-line": "compact",
        "sequence-style": "terminator",
        "single-case": "sparse",
        "space-around-arrays": "true",
        "space-around-lists": "true",
        "space-around-records": "true",
        "space-around-variants": "true",
        "stritem-extension-indent": None,
        "type-decl": "sparse",
        "type-decl-indent": None,
        "wrap-comments": "false",
        "wrap-fun-args": "false" }
}

# Requires a Github access token
# Will make a lot of requests to github

GITHUB_ACCESS_TOKEN = ""

def github_api_paged(url):
    res = requests.get(url, headers={ "Authorization": "token " + GITHUB_ACCESS_TOKEN })
    res.raise_for_status()
    res_data = res.json()
    yield from res_data["items"]
    if "next" in res.links:
        yield from github_api_paged(res.links["next"]["url"])

def url_raw_of_web(url):
    return re.sub(
            r'^https://github.com/([^/]+)/([^/]+)/blob/(.+)$',
            r'https://raw.githubusercontent.com/\1/\2/\3', url)

def get_ocamlformat_files():
    query = "https://api.github.com/search/code?q=filename:.ocamlformat&per_page=100"
    return [
            { "project": r["repository"]["full_name"],
              "download_url": url_raw_of_web(r["html_url"]),
              "score": r["score"] }
            for r in github_api_paged(query)
            if r["name"] == ".ocamlformat" ]

def fetch_files(results):
    for r in results:
        res = requests.get(r["download_url"])
        res.raise_for_status()
        r["content"] = res.content.decode("utf-8")

def parse_options(results):
    def parse_opt(line):
        ws = line.split("#")[0].split("=", 1)
        opt = ws[0].strip()
        val = ws[1].strip() if len(ws) == 2 else None
        # Ignore the value of options taking an int
        if opt in ALL_OPTIONS and ALL_OPTIONS[opt] is None:
            val = None
        return [ (opt, val) ] if opt != "" else []
    for r in results:
        r["options"] = { opt: val for line in r["content"].splitlines() for opt, val in parse_opt(line) }

# Number of projects using each pair option, value
# Print
def count_options(results):
    options_per_projects = {}
    for r in results:
        # Apply profile
        opts = { **ALL_PROFILES.get(r["options"].get("profile", "ocamlformat"), {}), **r["options"] }
        # opts = r["options"]
        options_per_projects.setdefault(r["project"], set()).update(opts.items())
    # count_per_options = {}
    # Set all possible pairs, so unused options will show in the result
    count_per_options = { (opt, val): 0 for opt, values in ALL_OPTIONS.items() for val in (values or [None]) }
    for pair in itertools.chain(*options_per_projects.values()):
        count_per_options.setdefault(pair, 0)
        count_per_options[pair] += 1
    # Add option from profile
    counts = sorted(count_per_options.items(), key=lambda i: i[1], reverse=True)
    print("Projects: %d, .ocamlformat files: %d" % (len(options_per_projects), len(results)))
    for pair, count in counts:
        opt, val = pair
        # print("%4d %s = %s" % (count, opt, val))
        print("%4d %s" % (count, opt if val is None else "%s = %s" % pair))

results = get_ocamlformat_files()
fetch_files(results)
parse_options(results)

count_options(results)
