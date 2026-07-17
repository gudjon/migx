---
id: arch-<domain>-<facet>
type: ddd-bounded-context
title: "<domain-facet> — <one-line responsibility>"
owns:
  - src/<path>/            # code paths this context is the single home for
exclude:                   # carved out to another context (name it)
  - src/<path>/sub/        # → arch-<other>
thread_domain: <rt-audio | gui | gpu-render | worker | any>
rt_safety: <hard | soft | none>       # hard = no alloc/lock/block on this path
subdomain: <core | supporting | generic>
upstream: []               # [arch-*] who feeds this context
downstream: []             # [arch-*] who this feeds
maturity: <scaffold | developing | operational | hardened>
fork_delta: <upstream-tracking | migx-divergent | migx-new>
agents_md: src/<domain>/AGENTS.md
last_audited: "YYYY-MM-DD"
---

# <domain-facet> — bounded context

> One paragraph: what this context is responsible for and where its edge is.
> Pointers, never copies — the code in `owns:` is the truth.

## Key aggregates / classes
| Class | File | Role |
|---|---|---|
| `<Class>` | `<path.cpp>` | <role> |

## Invariants (an agent MUST respect these)
- **<the RT/ownership/other invariant>** — <what it forbids / requires>. (cite `P-NN`)

## Ubiquitous language (terms precise *inside* this context)
| Term | Meaning here | Not to be confused with |
|---|---|---|
| `<term>` | <meaning> | <other meaning elsewhere> |

## Boundaries (edges by id — detail in ../boundaries/<slug>.md)
| Dir | Seam | Other context | Mechanism | Doc |
|---|---|---|---|---|
| in/out | <what crosses> | arch-<other> | <ControlObject / callback / ring buffer> | boundaries/<slug>.md |

## Key patterns (cited, not restated)
- `P-NN` — <why this context relies on it>. Root house rules: `/AGENTS.md`.
