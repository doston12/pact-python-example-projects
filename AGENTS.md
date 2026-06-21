# Repository Guidelines

## Project Structure & Module Organization

This repository contains independent pact-python example packages. `simple_get_example/` is the local-file Pact flow for `GET /orders`; `simple_get_broker_example/` is the same example adapted for Pact Broker. Each package keeps consumer code in `consumer/`, provider code in `provider/`, provider fixtures in `provider/data/`, generated contracts in `pacts/`, and helper runners at the package root. The root `docker-compose.pact-broker.yml` starts a local Pact Broker for broker-based workflows.

## Build, Test, and Development Commands

Install dependencies for the example you are working on:

```bash
python3 -m pip install -r simple_get_example/requirements.txt
python3 -m pip install -r simple_get_broker_example/requirements.txt
```

Run local-file consumer and provider tests:

```bash
python3 -m pytest simple_get_example/consumer simple_get_example/provider -q
```

Run the broker example tests:

```bash
python3 -m pytest simple_get_broker_example/consumer -q
python3 -m pytest simple_get_broker_example/provider -q
```

Start or stop the local Pact Broker:

```bash
docker compose -f docker-compose.pact-broker.yml up -d
docker compose -f docker-compose.pact-broker.yml down
```

## Coding Style & Naming Conventions

Use standard Python style with 4-space indentation, clear module names, and package-relative imports. Keep consumer models and clients under `consumer/`; keep Flask provider behavior under `provider/`. Name tests with `test_*.py` and test functions with `test_*` so pytest discovers them. Prefer explicit, readable names such as `order_client.py`, `test_consumer.py`, and `test_provider.py`.

## Testing Guidelines

The test framework is pytest. Consumer tests generate pact JSON files under each package's `pacts/` directory; provider tests verify those contracts against the Flask provider. When changing contract shape, run the relevant consumer test first to regenerate the pact, then run the provider verification. For broker verification, set `PACT_URL` or `PACT_BROKER_BASE_URL` and `PACT_PROVIDER_VERSION` as shown in the README.

## Commit & Pull Request Guidelines

Recent commits use short, imperative summaries such as `add an example with pact broker` and `Fix package-relative imports`. Keep commits focused and describe the user-visible or test behavior changed. Pull requests should include a concise description, the example package affected, commands run, and any Pact Broker setup needed to verify the change. Include screenshots only when changing documentation images or broker UI guidance.
