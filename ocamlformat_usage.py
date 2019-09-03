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
    "break-fun-sig": ["wrap", "Fit-or-vertical", "smart"],
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
    "wrap-fun-args": ["true", "false"]
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
        r["options"] = [ pair for line in r["content"].splitlines() for pair in parse_opt(line) ]

# Number of projects using each pair option, value
# Print
def count_options(results):
    options_per_projects = {}
    for r in results:
        options_per_projects.setdefault(r["project"], set()).update(r["options"])
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
