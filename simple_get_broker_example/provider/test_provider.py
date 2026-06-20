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

from ..pact_config import CONSUMER_NAME, PACT_DIR, PROVIDER_NAME
from .provider import create_app


def test_should_validate_the_expectations_of_order_web() -> None:
    # There are tools for sharing contracts between consumer and provider.
    # This broker example can retrieve the contract from Pact Broker and publish verification results.
    # It still supports the local pact directory as a fallback so the test remains runnable without Docker.
    pact_url = os.environ.get("PACT_URL")
    pact_broker_base_url = os.environ.get("PACT_BROKER_BASE_URL")

    # Start the real provider API server.
    # Provider verification needs the real provider running; Pact's mock server is only used by consumer tests.
    # if you want the flask server to run and play with: enter this command
    # python3 -m flask --app simple_get_broker_example.provider.provider:create_app run --host 127.0.0.1 --port 5000
    server = make_server("127.0.0.1", 0, create_app())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        # Create a pact verifier object and seed:
        # 1. Who is the provider (provider name) -- GettingStartedBrokerOrderApi
        # 2. Consumer-generated pact (contract) file or broker source
        # 3. Where is provider running (host and port) -- http://127.0.0.1:<random-port> -- 0 means get any free port
        host, port = server.server_address
        verifier = Verifier(PROVIDER_NAME, host=host).add_transport(url=f"http://{host}:{port}")

        if pact_broker_base_url:
            # Broker mode: retrieve the latest main-branch pact for this consumer/provider pair.
            (
                verifier.broker_source(pact_broker_base_url, selector=True)
                .consumer_version(
                    consumer=CONSUMER_NAME,
                    branch=os.environ.get("PACT_CONSUMER_BRANCH", "main"),
                    latest=True,
                )
                .build()
            )

            # If a provider version is supplied, pact-python publishes the verification result back to the broker.
            provider_version = os.environ.get("PACT_PROVIDER_VERSION")
            if provider_version:
                verifier.set_publish_options(
                    provider_version,
                    branch=os.environ.get("PACT_PROVIDER_BRANCH", "main"),
                )
        elif pact_url:
            # Direct URL mode: useful while learning the broker's pact retrieval endpoint.
            verifier.add_source(pact_url)
        else:
            verifier.add_source(Path(PACT_DIR))

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
