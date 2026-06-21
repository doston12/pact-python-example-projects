# Advanced Order Platform Pact Example

This package is a more production-ish Pact example than `simple_get_broker_example`.
It still stays small enough to study, but it demonstrates contract testing patterns
that become important when consumer and provider teams work independently.

Participants:

- Consumer: `AdvancedOrderWeb`
- Provider: `AdvancedOrderApi`

## What This Example Covers

- Multiple interactions in one pact file.
- Provider states with parameters, such as `order exists` with a specific `order_id`.
- Request headers for auth, request tracing, and idempotency.
- Auth contracts for valid tokens, missing tokens, expired tokens, and insufficient scopes.
- Query parameters for list filtering and pagination.
- Nested JSON body matching instead of exact hard-coded response values.
- Consumer-side domain error handling for provider `401`, `403`, and `404` responses.
- Provider verification against either local pact files, one Pact Broker pact URL, or the broker's latest branch pact.
- Publishing provider verification results back to Pact Broker when `PACT_PROVIDER_VERSION` is set.

## Project Layout

```text
advanced_order_platform/
  consumer/
    order.py            # consumer-owned domain models
    order_client.py     # real HTTP client code exercised by Pact consumer tests
    test_consumer.py    # consumer contracts
  provider/
    data/orders.py      # provider fixtures
    provider.py         # Flask API
    test_provider.py    # provider verification
  pacts/                # generated Pact files
```

## Install Dependencies

From the repository root:

```bash
python3 -m pip install -r advanced_order_platform/requirements.txt
```

## Run Local File Flow

Generate the consumer pact:

```bash
python3 -m pytest advanced_order_platform/consumer -q
```

Verify the provider against the generated local pact:

```bash
python3 -m pytest advanced_order_platform/provider -q
```

Or run both:

```bash
python3 -m pytest advanced_order_platform/consumer advanced_order_platform/provider -q
```

## Run With Pact Broker

Start the broker from the repository root:

```bash
docker compose -f docker-compose.pact-broker.yml up -d
```

Publish the generated pact:

```bash
pact broker publish advanced_order_platform/pacts \
  --consumer-app-version 1.0.0 \
  --branch main \
  --broker-base-url http://localhost:9292
```

Verify one exact broker pact URL:

```bash
PACT_URL=http://localhost:9292/pacts/provider/AdvancedOrderApi/consumer/AdvancedOrderWeb/latest \
  python3 -m pytest advanced_order_platform/provider -q
```

Verify through broker integration and publish provider verification results:

```bash
PACT_BROKER_BASE_URL=http://localhost:9292 \
PACT_PROVIDER_VERSION=1.0.0 \
  python3 -m pytest advanced_order_platform/provider -q
```

Stop the broker:

```bash
docker compose -f docker-compose.pact-broker.yml down
```

## Practice Ideas

1. Add a second consumer with different needs, such as `AdvancedOrderAdmin`.
2. Add a `PUT /orders/{id}/status` interaction with an invalid-transition error.
3. Add provider pending/WIP pact verification once you move this into real CI.
4. Break one field in `provider/provider.py`, run provider verification, and study the failure output.
5. Split auth into a dedicated identity provider contract if the order API stops owning auth decisions.
