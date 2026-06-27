
# About what you should and should NOT write in contract tests

  For a consumer contract test, the main job is:

  1. Define the request the consumer must send.
  2. Define the response shape the consumer depends on.
  3. Exercise the real consumer client against the Pact mock server.
  4. Add a few assertions that prove the consumer can actually use the response.


