# Public distribution preparation

The GHCR-named Linux amd64 image installs controlplane-api and the frozen runtime
dependency graph under /opt/api. It is a consumer base, not an API server: its
default command reports the library version and exits. Downstream images supply
their own process and configuration. No port, database or external service is
started by preparation checks.

PR and main CI prepare and inspect this image without registry write access.
The image is not pushed by this change. Subsequent TEST publication uses a moving
channel; build-input digests and diagnostic image IDs do not pin running services.
No Actions archives or package releases are published.

LICENSE and NOTICE are checked byte-for-byte in the wheel, rebuilt source archive
and prepared image. The installed distribution inventory includes upstream legal
texts and their hashes under /usr/share/doc/controlplane-api/third-party.
Missing legal texts, mismatched package versions or altered bundled bytes refuse
preparation. Existing runtime byte contracts and historical release records remain
unchanged; only the exact NOTICE metadata addition is normalized for comparison.

Reachable-history CI scans fetched origin branches, tags and HEAD, including ZIP
and wheel members and commit/tag text. Hosted-code observations remain reported
without deleting or rewriting history. Hidden/deleted refs, unreachable objects,
remote LFS bytes, external archives and unknown archive formats are not covered.
A passing automated scan is not blanket public-content or legal clearance.

Every retained image layer is inspected, including files hidden by later layers.
The only current-image scanner exception is the exact public Python signing
fingerprint in image metadata, documented by the
[official Python image recipe](https://github.com/docker-library/python/blob/master/3.13/slim-bookworm/Dockerfile).
Other values and runtime paths refuse. Scan reports containing values remain in
job-local scratch and are removed; logs contain only redacted coordinates/counts.

Remaining work under Infra #993 includes corresponding-source and replacement
checks for applicable dependencies, base-image source/legal review, historical
content classification, retained older-image inventory and TEST publication.
No visibility change, history rewrite or stable release is authorized here.
Integration/e2e stays in scheduled nightly CI. Private hosting and accounting
implementations remain outside the consumer image.

The initial retained-content inventory found 16 coordinates across older API
configuration/metrics blobs and three historical events wheels. These are
reported as provider-related observations, not automatically classified secrets.
The bytes remain retained and require separate content disposition.

The [source/replacement preparation](../licenses/SOURCES.md) records the locked
LGPL/MPL components, hash-bound source materials, offline replacement checks and
the verified libcrypt origin for psycopg-binary 3.3.6 and base review limits.
