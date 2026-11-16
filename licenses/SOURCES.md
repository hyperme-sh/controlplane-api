> Superseded: runtime images no longer download or include source archives.
> LICENSE/NOTICE and dependency legal texts remain. The records below describe
> prior builds and are retained for historical review, not current build steps.

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

The locked wheel's bundled libcrypt now has an exact upstream manylinux build
reference: archived psycopg run 35339446265/job 105581758837 names image
c163a278006f45883c117b4166b93cdc7b574b62e58292ed9e52879579841d77.
Its manifest/config pair binds the source version/hash to the original native
layer. Original and installed .text/.rodata sections match. This closes the
previous 3.3.6 mapping gap without substituting the different 3.3.7 build.
CI verifies that chain and carries libxcrypt 4.5.2 sources and license texts.
All mapped native sources are present; bit-identical native rebuilds are not claimed.

See BASE.md for base-image source/legal review. Publication remains uncleared;
no visibility change, history rewrite or registry push is part of this change.
