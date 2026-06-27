# Advanced Order Platform Contract CI

This sample is wired for a production-like Pact flow:

1. Consumer contract tests generate `advanced_order_platform/pacts/*.json`.
2. CI publishes those pacts to a durable Pact Broker with the consumer version and branch.
3. Provider verification fetches the latest consumer pact for the same branch.
4. pact-python publishes the provider verification result back to the broker when `PACT_PROVIDER_VERSION` is set.

## Broker Hosting

Yes, for a real pipeline you need a Pact Broker that both consumer and provider CI can reach. The broker must be durable, because it is the shared system of record for pacts and verification results.

Good options:

- Managed PactFlow for the least operational work.
- Self-hosted Pact Broker behind HTTPS and authentication.
- The existing `docker-compose.pact-broker.yml` only for local development and demos.

Do not use an unauthenticated public broker for production contracts.

## GitHub Secrets

Configure these repository or organization secrets:

```text
PACT_BROKER_BASE_URL=https://your-broker.example.com
PACT_BROKER_TOKEN=...
```

If your broker uses basic auth instead of a token, set:

```text
PACT_BROKER_BASE_URL=https://your-broker.example.com
PACT_BROKER_USERNAME=...
PACT_BROKER_PASSWORD=...
```

## GitHub Actions

The workflow is in:

```text
.github/workflows/advanced-order-platform-contracts.yml
```

On pull requests it runs consumer pact tests and uploads the generated pact as an artifact. It does not publish from pull requests because forked PRs usually cannot access secrets and publishing every PR pact can pollute a shared broker unless you deliberately enable pending/WIP pact workflows.

On pushes to `main` or `develop`, it:

```text
consumer tests -> publish pacts -> provider verification -> publish verification result
```

## Local Broker Flow

From `pact-python-example-projects`:

```bash
docker compose -f docker-compose.pact-broker.yml up -d
export PACT_BROKER_BASE_URL=http://localhost:9292
export PACT_CONSUMER_VERSION=local-consumer
export PACT_PROVIDER_VERSION=local-provider
export PACT_CONSUMER_BRANCH=main
export PACT_PROVIDER_BRANCH=main

python3 -m pytest advanced_order_platform/consumer -q
advanced_order_platform/scripts/publish_consumer_pacts.sh
advanced_order_platform/scripts/verify_provider_from_broker.sh
```

Then open `http://localhost:9292`.
