# Historical content and image review

The content review binds all 16 retained provider-related coordinates to Git
object and member SHA-256 hashes. Two configuration blobs declare old provider
settings, two metrics blobs mention a provider only in a boundary comment, and
12 payload/schema members in three events wheels retain provider-specific fields.
These classifications do not delete bytes or grant publication clearance. CI
refuses new/missing coordinates, changed bytes or unrecognized classifications.

The read-only historical-image workflow inventories the runtime GHCR namespace
and scans each selected Linux amd64 image across every retained layer without
executing old code. Tags are resolved and checked against manifest bytes; image
selection records digests only for review, never as running service pins. Existing
source scan exceptions require exact known source bytes and coordinates.

This repository's recent preparation jobs build disposable images but do not
push them. No successful registry publication digest is recorded by that path.
The current operator package API returned 404. A separate CI registry check uses
repository-scoped read access. Responses 401/403/404 are reported as unavailable,
not proof of absence or a passing image review. Its image job skips when nothing
can be selected; the logged publication status remains uncleared. Other failures
refuse CI. No registry access/settings changes are performed to work around this.

Scope excludes deleted or unknown untagged images, other registry namespaces and
platforms, hidden/deleted/unreachable refs and remote LFS data. Layer reports are
not reconstructed final filesystems. Known malformed compression fixtures and
the three-level archive parsing limit remain documented in licenses/BASE.md.
No visibility changes, history rewriting, image deletion or manual release is
part of this review. Moving TEST and scheduled nightly integration/e2e remain.
