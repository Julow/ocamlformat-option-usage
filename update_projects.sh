#!/usr/bin/env bash

# Update the list of projects from the packages installed on a switch

while read pkg v repo; do
  repo=${repo#\"}
  repo=${repo%\"}
  if [[ $repo = "" ]]; then continue; fi
  echo "$pkg;$v;$repo"
done < <(opam list --short --columns=name,version,dev-repo:) |
sort -t ';' -k 3 -u
