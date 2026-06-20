"""
True power of contract testing comes with provider verification. Remember that contract testing is a two-way street:
    - Consumer tests asks: Does my consumer code make the request I expect, and can it handle the response shape I expect
    - Provider test asks: Can the real provider API satisfy the contract that the consumer generated?

On consumer side, pact acted as a mock server provider.
Now, on provider side pact acts as a verifier (of the contract).


"""
import os
import threading
from pathlib import Path

from pact import Verifier
from werkzeug.serving import make_server

from ..pact_config import PACT_DIR, PROVIDER_NAME
from .provider import create_app


def test_should_validate_the_expectations_of_order_web() -> None:
    # There are tools for sharing contracts between consumer and provider.
    # For example, when the provider is a separate company, you can use Pact Broker to share the contract.
    # This simple example skips contract sharing and loads the generated pact from the local directory.
    pact_url = os.environ.get("PACT_URL")
    pact_source = Path(pact_url) if pact_url else PACT_DIR

    # Start the real provider API server.
    # Provider verification needs the real provider running; Pact's mock server is only used by consumer tests.
    # if you want the flask server to run and play with: enter this command
    # python3 -m flask --app simple_get_example.provider.provider:create_app run --host 127.0.0.1 --port 5000
    server = make_server("127.0.0.1", 0, create_app())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        # Create a pact verifier object and seed:
        # 1. Who is the provider (provider name) -- GettingStartedOrderApi
        # 2. Consumer-generated pact (contract) file -- ./pacts/GettingStartedOrderWeb-GettingStartedOrderApi.json
        # 3. Where is provider running (host and port) -- http://127.0.0.1:<random-port> -- 0 means get any free port
        host, port = server.server_address
        verifier = (
            Verifier(PROVIDER_NAME, host=host)
            .add_source(str(pact_source))
            .add_transport(url=f"http://{host}:{port}")
        )

        # Pact replays the contract against the real provider. This is the main point of the test.
        # Pact reads the contract file, and sends GET request to /orders endpoint(which is locally running in Flask app)
        # Then it checks the real response against the contract:
        # - Does the real provider respond with 200 OK?
        # - Does the real provider respond with Content-Type: application/json; charset=utf-8?
        # - Does the real provider respond with the expected JSON body?
        # If all of these checks pass, the provider verification is successful.
        # If any of these checks fail, the provider verification fails.
        verifier.verify()
    finally:
        # shutdown the server once tests complete
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
