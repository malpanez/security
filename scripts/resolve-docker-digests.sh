#!/bin/bash
set -euo pipefail

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to parse registry tokens" >&2
  exit 1
fi

get_digest() {
  local image=$1
  local repo=${image%%:*}
  local tag=${image##*:}
  if [[ "${repo}" != */* ]]; then
    repo="library/${repo}"
  fi
  local token
  token=$(curl -sSfL "https://auth.docker.io/token?service=registry.docker.io&scope=repository:${repo}:pull" \
    | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])')
  curl -sSI -H "Authorization: Bearer ${token}" \
    -H "Accept: application/vnd.docker.distribution.manifest.list.v2+json" \
    "https://registry-1.docker.io/v2/${repo}/manifests/${tag}" \
    | awk -F': ' 'tolower($1)=="docker-content-digest" {print $2}' \
    | tr -d '\r'
}

images=(
  "geerlingguy/docker-ubuntu2204-ansible:latest"
  "geerlingguy/docker-ubuntu2004-ansible:latest"
  "geerlingguy/docker-debian13-ansible:latest"
  "geerlingguy/docker-debian12-ansible:latest"
  "geerlingguy/docker-debian11-ansible:latest"
  "geerlingguy/docker-rockylinux9-ansible:latest"
  "geerlingguy/docker-rockylinux8-ansible:latest"
  "ubuntu:22.04"
  "ubuntu:20.04"
  "debian:12"
  "debian:11"
  "rockylinux:9"
  "rockylinux:8"
  "redhat/ubi9:latest"
  "redhat/ubi8:latest"
)

for image in "${images[@]}"; do
  digest=$(get_digest "${image}")
  echo "${image}@${digest}"
done
