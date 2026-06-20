import sys
from pathlib import Path

import pytest

from .pact_config import PACT_FILE


def run_tests(test_type: str) -> int:
    test_dir = Path(__file__).resolve().parent / test_type
    result = pytest.main([str(test_dir), "-q"])

    if result:
        print(f"{test_type} test failed :(")
    else:
        print(f"{test_type} test passed! Open the pact file in {PACT_FILE}")

    return int(result)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"consumer", "provider"}:
        print("Usage: python -m simple_get_example.run_test <consumer|provider>")
        raise SystemExit(2)

    raise SystemExit(run_tests(sys.argv[1]))
