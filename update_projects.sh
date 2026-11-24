#!/usr/bin/env bash

# Update the project list.
opam list --all --columns=package --short | sort > projects
