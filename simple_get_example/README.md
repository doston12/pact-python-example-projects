# Pact Python example projects

This is a collection of pact-python example tests/projects showing how to implement different test strategies with detailed explanations of their tradeoffs.

## Simple GET Example

This package is a Python equivalent of the Pact 5 minute guide. It is the first small example project in this repository and demonstrates a simple `GET /orders` contract.

It contains:

- `consumer/order.py`: typed `Order` and `OrderItem` dataclass models.
- `consumer/order_client.py`: client that calls `GET /orders` and returns `Order` objects.
- `provider/provider.py`: local Order API provider using Flask.
- `consumer/test_consumer.py`: consumer contract test that writes `pacts/GettingStartedOrderWeb-GettingStartedOrderApi.json`.
- `provider/test_provider.py`: provider verification test that reads the pact and verifies the local provider.

Run it:

Install the Python test/runtime dependencies first if needed:

```bash
python3 -m pip install -r requirements.txt
```

From the repository root, run the tests directly with pytest:

```bash
python3 -m pytest simple_get_example/consumer -q
python3 -m pytest simple_get_example/provider -q
```

Or run both test suites together:

```bash
python3 -m pytest simple_get_example/consumer simple_get_example/provider -q
```

The `run_consumer_test.py`, `run_provider_test.py`, and `run_test.py` files are helper scripts only. They mirror the JavaScript example's runner files and call pytest for you, but Pact does not require them.

```bash
python3 -m simple_get_example.run_consumer_test
python3 -m simple_get_example.run_provider_test
python3 -m simple_get_example.run_test consumer
python3 -m simple_get_example.run_test provider
```
