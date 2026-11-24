#!/usr/bin/env bash

# Update the project list. It is computed from the list in 'opam_repo_logs',
# which was obtained by running in opam-repository:
# git log --since="1 years ago" --name-only --pretty=format: | sort -u > opam_repo_logs

# Keep the last version of each packages
declare -A pkgs

while read path; do
  if [[ $path =~ ^packages/([^/]+)/([^/]+)/opam$ ]]; then
    pkg_name=${BASH_REMATCH[1]}
    pkg_namever=${BASH_REMATCH[2]}
    pkgs["$pkg_name"]="$pkg_namever"
  fi
done < opam_repo_logs

for pkg_name in "${!pkgs[@]}"; do
  echo "${pkgs["$pkg_name"]}"
done > projects

echo "Wrote ${#pkgs[@]} projects to 'projects'"
