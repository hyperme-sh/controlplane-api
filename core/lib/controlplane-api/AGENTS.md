# controlplane-api package context

Shared configuration, logging, exceptions, utilities, event names, metrics, CORS,
health/version endpoints, permissions and process-local operator plugin registration.
Public modules are exact declarations in scripts/import_boundaries.json and
scripts/ownership.json. Import no legacy api or product implementation.
Keep api compatibility aliases as the same module objects so settings, counters,
router state and monkeypatches stay shared. Portal controls belong to identity.
The current deployment's operator plugin declarations live under config; new
trusted plugins use register_plugin. Preserve existing HTTP routes and payloads.
Run the shared and affected service suites; wheel/alias tests live in core/tests.
