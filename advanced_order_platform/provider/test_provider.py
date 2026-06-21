import os
import threading
from pathlib import Path
from typing import Any

from pact import Verifier
from werkzeug.serving import make_server

from ..pact_config import CONSUMER_NAME, PACT_DIR, PROVIDER_NAME
from .data.orders import MISSING_ORDER_ID, OPEN_ORDER_ID
from .provider import (
    create_app,
    ensure_order_exists,
    ensure_order_missing,
    register_access_token,
    reset_auth_policy,
    reset_data_store,
)


def reset_provider_state() -> None:
    reset_data_store()
    reset_auth_policy()


def provider_state_handler(
    state: str,
    action: str,
    parameters: dict[str, Any] | None = None,
) -> None:
    if action == "teardown":
        reset_provider_state()
        return

    parameters = parameters or {}
    if state == "open orders exist":
        reset_provider_state()
    elif state == "order exists":
        reset_provider_state()
        ensure_order_exists(str(parameters.get("order_id", OPEN_ORDER_ID)))
    elif state == "the customer can place orders":
        reset_provider_state()
    elif state == "order does not exist":
        reset_provider_state()
        ensure_order_missing(str(parameters.get("order_id", MISSING_ORDER_ID)))
    elif state == "a valid access token exists":
        reset_provider_state()
        register_access_token(
            str(parameters.get("token", "test-token")),
            active=True,
            scopes={"orders:read", "orders:write"},
        )
    elif state == "no access token is provided":
        reset_provider_state()
    elif state == "the access token is expired":
        reset_provider_state()
        register_access_token(
            str(parameters.get("token", "expired-token")),
            active=False,
            scopes={"orders:read", "orders:write"},
        )
    elif state == "the access token cannot read orders":
        reset_provider_state()
        register_access_token(
            str(parameters.get("token", "write-only-token")),
            active=True,
            scopes={"orders:write"},
        )
    else:
        reset_provider_state()


def test_should_validate_the_expectations_of_order_web() -> None:
    pact_url = os.environ.get("PACT_URL")
    pact_broker_base_url = os.environ.get("PACT_BROKER_BASE_URL")

    server = make_server("127.0.0.1", 0, create_app())
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        verifier = (
            Verifier(PROVIDER_NAME, host=host)
            .add_transport(url=f"http://{host}:{port}")
            .state_handler(provider_state_handler, teardown=True)
        )

        if pact_broker_base_url:
            (
                verifier.broker_source(pact_broker_base_url, selector=True)
                .consumer_version(
                    consumer=CONSUMER_NAME,
                    branch=os.environ.get("PACT_CONSUMER_BRANCH", "main"),
                    latest=True,
                )
                .build()
            )

            provider_version = os.environ.get("PACT_PROVIDER_VERSION")
            if provider_version:
                verifier.set_publish_options(
                    provider_version,
                    branch=os.environ.get("PACT_PROVIDER_BRANCH", "main"),
                )
        elif pact_url:
            verifier.add_source(pact_url)
        else:
            verifier.add_source(Path(PACT_DIR))

        verifier.verify()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
