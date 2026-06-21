from pathlib import Path


CONSUMER_NAME = "AdvancedOrderWeb"
PROVIDER_NAME = "AdvancedOrderApi"
CONSUMER_VERSION = "1.0.0"

PACT_DIR = Path(__file__).resolve().parent / "pacts"
PACT_FILE = PACT_DIR / f"{CONSUMER_NAME}-{PROVIDER_NAME}.json"
