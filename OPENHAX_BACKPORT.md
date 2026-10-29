# OpenHAX 2.14.5 compatibility backport

Copyright (C) 2026 OpenHAX contributors. This process document is
GPL-3.0-or-later; library licensing is described in LICENSING.md.

This branch validates its committed uv.lock on its declared Python matrix.
It preserves the complete upstream test selections, including the separate
client-process and integration jobs. CI installs that supported locked
backport stack rather than claiming support for arbitrary future resolver
upgrades. No test is removed, no xfail is added, and no failed forward
resolution is converted to a passing result.

The initial unbounded upgrade run 40969752107 at a7f197b507e570997909cc59c385f9301e262cb8
remains native negative evidence: newer transitive Anthropic/MCP/schema and
proxy behavior differs from the reviewed lock. That observation is separate
from the successful source wheel/full-suite run 40969751181. Package metadata
can permit other resolver choices; this backport makes no whole-suite claim
for those choices. Consumers such as Cloud Cuckoo lock and qualify their own
actual dependency graph and runtime separately.

The minimum runtime is Python 3.11 because the maintained HTTPX2 integration
requires it. The original repository development selection remains Python 3.12.
The upstream-owned Marvin App triage job runs only in PrefectHQ/fastmcp,
without introducing substitute credentials in this fork.
