#!/usr/bin/env bash

mkdir -p pkgs

while read pkgver; do
  dst="pkgs/$pkgver"
  if ! [[ -e $dst ]]; then
    opam source --dir="$dst" "$pkgver"
  fi
done < projects

ocaml ocamlformat_usage.ml > output
