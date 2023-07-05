#!/usr/bin/env bash

mkdir -p pkgs

while IFS=';' read name v url; do
  pkg="$name.$v"
  dst="pkgs/$pkg"
  if ! [[ -e $dst ]]; then
    opam source --dir="$dst" "$pkg"
  fi
done < projects

ocaml ocamlformat_usage.ml > output
