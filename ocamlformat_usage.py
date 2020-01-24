import requests
import json
import re
import itertools
import sys

from all_options import OPTIONS, PROFILES

# Requires a Github access token
# Will make a lot of requests to github

GITHUB_ACCESS_TOKEN = ""

def github_api_paged(url):
    print("GET %s" % url, file=sys.stderr)
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
    print("Fetching %d .ocamlformat files" % len(results), file=sys.stderr)
    for r in results:
        res = requests.get(r["download_url"])
        res.raise_for_status()
        r["content"] = res.content.decode("utf-8")

def parse_options(results):
    def parse_opt(line):
        ws = line.split("#")[0].split("=", 1)
        opt = ws[0].strip()
        val = ws[1].strip() if len(ws) == 2 else None
        return [ (opt, val) ] if opt != "" else []
    for r in results:
        r["options"] = { opt: val for line in r["content"].splitlines() for opt, val in parse_opt(line) }

# Number of projects using each pair option, value
# Print
def count_options(results):
    options_per_projects = {}
    for r in results:
        # Apply profile
        opts = { **PROFILES.get(r["options"].get("profile", "default"), {}), **r["options"] }
        # opts = r["options"]
        options_per_projects.setdefault(r["project"], set()).update(opts.items())
    # count_per_options = {}
    # Set all possible pairs, so unused options will show in the result
    count_per_options = { (opt, val): 0 for opt, values in OPTIONS.items() for val in values }
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

try:
    with open("cache", "r") as f:
        print("Using cached results from file 'cache'", file=sys.stderr)
        results = json.load(f)
except FileNotFoundError:
    results = get_ocamlformat_files()
    fetch_files(results)
    with open("cache", "w") as f:
        json.dump(results, f)

parse_options(results)

count_options(results)
