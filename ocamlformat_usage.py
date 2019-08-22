import requests
import json
import re
import itertools

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

def clean_options(results):
    def clean_line(l):
        return " = ".join(map(str.strip, l.split("#")[0].split("=", 1)))
    for r in results:
        r["options"] = filter(bool, map(clean_line, r["content"].splitlines()))

# Number of projects using each pair option, value
# Print
def count_options(results):
    options_per_projects = {}
    for r in results:
        options_per_projects.setdefault(r["project"], set()).update(r["options"])
    count_per_options = {}
    for opt in itertools.chain(*options_per_projects.values()):
        count_per_options.setdefault(opt, 0)
        count_per_options[opt] += 1
    counts = sorted(count_per_options.items(), key=lambda i: i[1], reverse=True)
    for option, count in counts:
        print("%4d %s" % (count, option))

results = get_ocamlformat_files()
fetch_files(results)
clean_options(results)

count_options(results)