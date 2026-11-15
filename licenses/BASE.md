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

Debian source references are derived from installed Source/Version fields,
including explicit source versions where binary rebuild versions differ. They
identify the required source-package versions; the Debian source archives have
not yet been bundled or rebuilt. This is a measured legal/source inventory,
not a complete corresponding-source distribution or blanket publication clearance.
Older-image and retained historical-content reviews remain separate.

The wheel's bundled libcrypt and Debian's libcrypt1 are different components.
The former is verified through the upstream manylinux image and libxcrypt 4.5.2;
the latter is recorded as Debian libxcrypt 1:4.4.33-2 in the base inventory.
Build identities are provenance, not running TEST service pins. TEST remains on
moving channels, and integration/e2e stays in scheduled nightly CI.
