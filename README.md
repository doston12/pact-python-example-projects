# Pact Python example projects

This is a collection of pact-python example tests/projects showing how to implement different test strategies with detailed explanations of their tradeoffs.

## Python copy of the Pact 5 minute guide

This directory is a Python equivalent of the JavaScript example in the project root.

It mirrors the original layout:

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

Run the tests directly with pytest:

```bash
python3 -m pytest consumer -q
python3 -m pytest provider -q
```

Or run both test suites together:

```bash
python3 -m pytest consumer provider -q
```

The `run_consumer_test.py`, `run_provider_test.py`, and `run_test.py` files are helper scripts only. They mirror the JavaScript example's runner files and call pytest for you, but Pact does not require them.

```bash
cd ..
python3 -m python_copy.run_consumer_test
python3 -m python_copy.run_provider_test
```
