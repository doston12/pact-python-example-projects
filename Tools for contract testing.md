# Tools for Contract Testing

Pact and Spring Cloud Contract are two of the most commonly discussed tools for contract testing. Other tools may be a 
better fit for specific use cases. For example, if you are doing OpenAPI-based contract testing, consider tools such as
Schemathesis, Dredd, or Specmatic.


## Pact vs Spring Cloud Contract

The main differences between Pact and Spring Cloud Contract (SCC) are:

- **Pact** focuses more on consumer-driven contract testing.
- **Spring Cloud Contract** focuses more on provider-driven contract testing.
- Pact contracts are language agnostic. For example, you can write consumer contract tests in JavaScript, generate a 
  Pact contract file, and the provider whose stack either python or java can verify it without any issues.



## Other Contract Testing Tools

- **Schemathesis**: useful for testing APIs from OpenAPI or GraphQL schemas.
- **Dredd**: validates API implementations against API description documents.
- **Specmatic**: supports contract testing and service virtualization from API specifications.
