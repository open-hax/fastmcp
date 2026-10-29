# OpenHAX compatibility fork licensing

This fork starts at upstream commit `21221b4ab128e8dd71b5d9637fa70a9139511380`. The original `LICENSE` is
retained byte for byte, along with all original copyright/license notices.
Upstream code remains available under Apache-2.0. No upstream author is
represented as relicensing their contribution.

OpenHAX-authored modifications for JWT issuer/provider adaptation and compatibility integration
are Copyright (C) 2026 OpenHAX contributors and licensed under the GNU
Lesser General Public License, version 3 or (at your option) any later
version. The full LGPL terms are in `COPYING.LESSER`; the incorporated
GNU GPL version 3 terms are in `COPYING`. Original upstream code and
copied upstream patches retain their Apache-2.0 terms.

The combined distribution therefore declares `Apache-2.0 AND
LGPL-3.0-or-later`, requiring preservation of both applicable sets of
notices and terms. This is a library compatibility fork, with its own
PEP 440 local version; it is not an official upstream release.

The modification boundary is the OpenHAX-authored changes to runtime files,
compatibility metadata, regression tests and fork documentation in this
branch, as shown by its Git diff from the upstream base. `NOTICE` names
the upstream provenance of copied patches. Existing unmodified repository
files remain under their original terms. Fork CI/process documentation is
provided under GPL-3.0-or-later.
