#!/usr/bin/env bash

set -e

mkdir -p pkgs

while read pkgver; do
  dst="pkgs/$pkgver"
  if ! [[ -e $dst ]]; then
    opam source --dir="$dst" "$pkgver" || mkdir "$dst"
  fi
done < projects

ocaml ocamlformat_usage.ml > output
