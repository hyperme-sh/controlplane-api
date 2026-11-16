> Superseded: runtime images no longer download or include source archives.
> LICENSE/NOTICE and dependency legal texts remain. The records below describe
> prior builds and are retained for historical review, not current build steps.

# Python base source/legal review

base-image.json records the exact Linux amd64 Python image already used by the
consumer build. Four original base-layer identities, the final dpkg status bytes,
97 installed binary/source-version pairs and 115 legal-file hashes are verified.
Copyright symlinks are resolved within the filesystem; inherited copyright and
common-license files stay in their original locations. Changes refuse CI.

CPython 3.13.18 source is included in the image and hash-checked against the
upstream base configuration. Its LICENSE is byte-identical to the installed
/usr/local/lib/python3.13/LICENSE.txt. The single source-scan exception is a
literal private-key placeholder in upstream ssl documentation, bound to exact
archive/member hashes, rule and line; no actual key is present.

Debian sources are bundled under /usr/share/doc/controlplane-api/debian-sources.
The 97 installed binaries map to 69 exact source-version pairs. The bundle carries
all 69 descriptors and all 153 referenced archives, including patches and upstream
signatures where the descriptors list them. Each descriptor's Source/Version and
Checksums-Sha256 fields are checked against the complete source inventory and
actual file bytes. Missing or changed records refuse preparation.

Descriptor signatures are retained; this check does not establish a Debian signer
trust chain or claim a bit-identical rebuild. Hashes and official mirror origins
bind the reviewed materials. Publication clearance remains separate.
Older-image and retained historical-content reviews remain separate.

The wheel's bundled libcrypt and Debian's libcrypt1 are different components.
The former is verified through the upstream manylinux image and libxcrypt 4.5.2;
the latter is recorded as Debian libxcrypt 1:4.4.33-2 in the base inventory.
Build identities are provenance, not running TEST service pins. TEST remains on
moving channels, and integration/e2e stays in scheduled nightly CI.

Static source scanning classified 7,396 matches in exact public Debian archives:
cryptographic test/demo keys and PKCS#12 fixtures, public signing fingerprints,
documentation examples and code identifiers. Exceptions require the entire
archive hash plus the full nested member path, rule and start/end coordinates.
Changed bytes, other coordinates and runtime paths refuse. Archives remain
unchanged. The pinned scanner processes up to three archive levels; malformed
compression fixtures in compression-library tests cannot be recursively decoded.
Their retained bytes remain bound to reviewed archive hashes; no exhaustive
parsing of malformed streams is claimed.
