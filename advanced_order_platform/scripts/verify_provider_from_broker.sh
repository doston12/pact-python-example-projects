#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${PACT_BROKER_BASE_URL:-}" ]]; then
  echo "PACT_BROKER_BASE_URL is required to verify provider pacts from the broker." >&2
  exit 1
fi

export PACT_PROVIDER_VERSION="${PACT_PROVIDER_VERSION:-${GITHUB_SHA:-local-dev}}"
export PACT_PROVIDER_BRANCH="${PACT_PROVIDER_BRANCH:-${GITHUB_REF_NAME:-main}}"
export PACT_CONSUMER_BRANCH="${PACT_CONSUMER_BRANCH:-${GITHUB_REF_NAME:-main}}"

python3 -m pytest advanced_order_platform/provider -q
