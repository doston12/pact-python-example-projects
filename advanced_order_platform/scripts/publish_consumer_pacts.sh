#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${PACT_BROKER_BASE_URL:-}" ]]; then
  echo "PACT_BROKER_BASE_URL is required to publish pacts." >&2
  exit 1
fi

consumer_version="${PACT_CONSUMER_VERSION:-${GITHUB_SHA:-local-dev}}"
consumer_branch="${PACT_CONSUMER_BRANCH:-${GITHUB_REF_NAME:-main}}"
pact_dir="${PACT_DIR:-advanced_order_platform/pacts}"

auth_args=()
if [[ -n "${PACT_BROKER_TOKEN:-}" ]]; then
  auth_args+=(--broker-token "${PACT_BROKER_TOKEN}")
elif [[ -n "${PACT_BROKER_USERNAME:-}" ]]; then
  auth_args+=(--broker-username "${PACT_BROKER_USERNAME}")
  auth_args+=(--broker-password "${PACT_BROKER_PASSWORD:-}")
fi

pact broker publish "${pact_dir}" \
  --consumer-app-version "${consumer_version}" \
  --branch "${consumer_branch}" \
  --broker-base-url "${PACT_BROKER_BASE_URL}" \
  "${auth_args[@]}"
