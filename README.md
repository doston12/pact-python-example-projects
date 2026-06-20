# Pact Python example projects

This repository contains separate pact-python example projects. Each example lives in its own Python package so it can be run independently.

## Examples

- `simple_get_example`: first small example showing a consumer contract test and provider verification for `GET /orders`.

Run an example from the repository root:

```bash
python3 -m pip install -r simple_get_example/requirements.txt
python3 -m pytest simple_get_example/consumer simple_get_example/provider -q
```
