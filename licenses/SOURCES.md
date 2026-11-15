# Source and replacement preparation

The locked consumer image includes certifi 2026.10.23 (MPL-2.0) and psycopg /
psycopg-binary 3.3.6 (LGPL-3.0). No jwcrypto or orjson is in this runtime graph.
The container carries hash-checked source archives and the upstream build recipe
under /usr/share/doc/controlplane-api/sources. sources.json binds package versions,
native member hashes and the wheel SBOM to the reviewed source inputs. Unchanged
GPL-3.0 text supplements the LGPL texts preserved from the installed packages.

CI checks recipient-modified certifi and an ABI-compatible modified libpq through
read-only mounts with networking disabled. It starts no service or database.
This is a replacement-loading contract, not a complete native rebuild.

The locked wheel's bundled libcrypt has different code sections from the prior
3.3.7 preparation. Its exact source/build origin remains unresolved and is
reported explicitly; the earlier provenance is not reused. Publication remains
uncleared. Base-image source/legal work and historical-content/older-image review
are separate follow-ups. No visibility or history changes are made here.
