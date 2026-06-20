

In simple terms, pact broker does the following:

    Consumer company publishes pact JSON
            ↓
    Pact Broker stores it
            ↓
    Provider company pulls pact JSON (during CI)
            ↓
    Provider verifies the pact (runs provider tests)
            ↓
    Verification result is published back to Broker (pass / fail)

Pact Broker is designed to share pacts and verification results between projects, and the verification tool can publish pass/fail results 
back so both sides can see whether the provider satisfies the consumer contract.




## Considerations for Sharing Pact Contracts

When sharing pact contracts between different teams or organizations, there are several considerations to keep in mind:
  - Who hosts it?
  - Who pays for it?
  - Which company manages users/secrets?
  - Can both CI systems access it?
  - Can both companies see all contracts?
  - Do you need IP allowlisting/VPN/private networking?

For a simple learning project, running the broker at `http://localhost:9292` without authentication is fine because everything is local.
In production, especially when two different companies collaborate, the Pact Broker should be treated like a shared internal API or artifact
registry. It should not be exposed as an unauthenticated public URL.

Common production setups:

- Use managed PactFlow.
  This is often the easiest option for cross-company collaboration. PactFlow provides hosted broker functionality with users, teams,
  API tokens, permissions, and auditability.

- Self-host the Pact Broker behind HTTPS and authentication.
  The broker might be available at a URL like `https://pact-broker.company.com`, usually behind Nginx, a load balancer,
  Kubernetes ingress, API gateway, VPN, or private network. Authentication can be basic auth for small internal setups,
  or SSO/OIDC/SAML through a reverse proxy for larger organizations.

- Let one company host the broker and give the other company scoped access.
  The external company should only receive access to the pacticipants/contracts they need. CI systems should use secrets,
  not personal credentials.

CI pipelines usually authenticate with broker credentials or tokens, for example:

```bash
PACT_BROKER_BASE_URL=https://pact-broker.company.com
PACT_BROKER_TOKEN=...
```

The practical rule is: local broker with no auth is good for learning; production broker needs HTTPS, authentication,
scoped authorization, secret rotation, and controlled network access.
