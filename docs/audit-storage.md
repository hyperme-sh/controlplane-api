# Audit temporary storage

Audit files live under `$TMPDIR/controlplane-api-<effective uid>` (the system
Python temporary directory when TMPDIR is unset). The directory must be owned
by the process user with mode 0700. Files must be regular, owned by that user,
mode 0600 and have one link. Reads and appends use a directory descriptor and
no-follow flags; links, FIFOs and unsafe permissions are refused. No existing
file or directory is silently repaired. Logs remain temporary storage; retention
and durable log export belong to the application operator.

`create_temp_file` retains its path-only behavior for existence checks. It
accepts only a bounded single filename and never returns a path in the shared
temporary root. Audit writers use the descriptor-based `audit_files.open_file`
API. Audit readers must use `log_paths(tenant_id)` and `open_file(path.name)`
rather than a hard-coded `/tmp` glob. Tenant identifiers allow only bounded
ASCII letters, digits, underscores and hyphens; tenant content never becomes
path syntax or a glob expression.

## Caller assessment

The API package's only caller of `create_temp_file` was its audit writer. Core's
compatibility module re-exports that helper. Core's read middleware builds audit
entries from the resolved user's tenant; repository writes accept `AuditLogDto`,
whose tenant field is an optional string rather than a UUID validator. The
helper therefore validates at the file boundary even when callers validate
identity earlier. Core's audit reader must adopt the shared storage helper and
the matching API pin together.

The archived monorepo contains older copies plus a reference seeder that uses
path existence as a lock check. Those copies are not modified by this package
change. Source inspection does not establish that arbitrary request input can
reach a deployed writer, or that deployed copies have adopted this fix. No live
host check or schema operation is part of this change.
