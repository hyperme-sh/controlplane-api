# controlplane-api

Installable shared API scaffolding: `config`, `logging`, `exceptions`, `utils`,
`event_types`, `metrics`, `service_cors`, `health`, `version`, `permissions`,
`operator.plugins` and supporting DTOs. Current services import these modules;
legacy `api.*` imports alias the same implementations. The package imports no
legacy API or product implementation and works as an isolated installed wheel.

The process owns one settings instance, Prometheus registry and router set.
Settings bind the identity library as before; portal controls remain in
`controlplane_identity`. Plugin registration accepts trusted local declarations,
rejects duplicate IDs and returns independent copies. Current plugin descriptors
remain configuration with the same IDs, permissions, actions and ordering.
The existing edge catalog health probe and version fallbacks remain compatible.

Public modules, the six-library source train and API snapshots advance to 0.10.0
because new module paths and plugin registration are public API additions. Service
and family ticket versions stay unchanged; this change publishes no packages.
The existing #299 outbox metrics table exception follows its moved source file.
