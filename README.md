# Pact Python example projects

This repository contains separate pact-python example projects. Each example lives in its own Python package so it can be run independently.

## Examples

- `simple_get_example`: first small example showing a consumer contract test and provider verification for `GET /orders`.
- `simple_get_broker_example`: copy of the simple GET example showing how to publish and verify pacts through Pact Broker.

Run an example from the repository root:

```bash
python3 -m pip install -r simple_get_example/requirements.txt
python3 -m pytest simple_get_example/consumer simple_get_example/provider -q
```

## Learning Pact Broker

`simple_get_example` intentionally keeps the beginner local-file flow. Use `simple_get_broker_example` when you want to
learn how the consumer and provider share the pact through Pact Broker.

The basic flow is:

1. The consumer test generates a pact JSON file.
2. The consumer publishes that file to Pact Broker with a consumer application version and branch.
3. The provider verification retrieves the pact from Pact Broker and runs it against the real provider.
4. The provider can publish the verification result back to Pact Broker with a provider application version.

Start a local Pact Broker:

```bash
# Start Docker Desktop first if the Docker daemon is not already running.
docker compose -f docker-compose.pact-broker.yml up -d
open http://localhost:9292
```

The compose file sets `PACT_BROKER_BASE_URL` to `http://localhost:9292` so the
broker UI, generated links, and host-run Pact CLI commands all use the same URL.

If you already started the broker before this setting existed, recreate the
container so the environment variable is applied:

```bash
docker compose -f docker-compose.pact-broker.yml up -d --force-recreate
```

Generate the pact from the consumer test:

```bash
python3 -m pytest simple_get_broker_example/consumer -q
```

Install the Pact unified CLI on your host machine if `pact` is not already on
your PATH:

```bash
brew tap pact-foundation/tap
brew install pact-foundation/tap/pact
pact --help
```

If you are not using Homebrew, install with Pact's official script:

```bash
curl -fsSL https://raw.githubusercontent.com/pact-foundation/pact-cli/main/install.sh | sh
```

Publish the pact to the broker from the host machine:

```bash
pact broker publish simple_get_broker_example/pacts \
  --consumer-app-version 1.0.0 \
  --branch main \
  --broker-base-url http://localhost:9292
```

Verify the provider by reading one exact pact URL back from the broker:

```bash
PACT_URL=http://localhost:9292/pacts/provider/GettingStartedBrokerOrderApi/consumer/GettingStartedBrokerOrderWeb/latest \
  python3 -m pytest simple_get_broker_example/provider -q
```

Or use pact-python's broker integration. This is the more realistic provider-side flow: pact-python asks the broker for
the latest `main` branch pact, verifies it, and publishes the provider verification result during the same test run when
`PACT_PROVIDER_VERSION` is set.

```bash
PACT_BROKER_BASE_URL=http://localhost:9292 \
PACT_PROVIDER_VERSION=1.0.0 \
  python3 -m pytest simple_get_broker_example/provider -q
```

These two provider commands are alternatives. There is no separate "publish provider results" CLI command here because
the provider verifier owns that result: it knows which pact was verified, which provider version passed or failed, and
uploads that result back to the broker as part of verification.

Stop the broker when you are done:

```bash
docker compose -f docker-compose.pact-broker.yml down
```
