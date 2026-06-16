---
name: pre-mortem
description: >-
  Imagine how a proposed change will break in production before writing the
  code. Use this skill whenever the user says "pre-mortem", "premortem", "what
  could break", "failure modes", "how will this fail", or after a plan has
  been approved but before implementation begins for any change touching
  shared state, payments, migrations, concurrency, auth, or external
  integrations. Also trigger proactively when the user is about to ship a
  multi-file change, when the change affects production data, or when "what
  could go wrong" is the right question to ask before code. The skill
  produces 3-5 ranked failure modes with likelihood, blast radius, and
  concrete mitigation, then a single recommendation: ship as-is, harden
  first, or split the change.
metadata:
  author: webreactiva.com
  namespace: webreactiva
---


# Pre-Mortem

Imagine the change has already shipped — and broken. You are reading the post-mortem the morning after the incident. Why did it fail?

This skill exists because the cheapest place to find a bug is in your imagination, not in production. The most expensive bugs come from confident-but-incomplete implementations: unit conversions assumed (minutes vs seconds), simultaneous webhook race conditions, mid-flight migrations breaking running jobs, scope creep removing a `DialogTitle` someone depended on. Each was foreseeable with five minutes of "how could this be wrong?". Pre-mortem is those five minutes, made structural.

## How this fits with the rest of the workflow

Pre-mortem sits between *plan approved* and *first commit*:

- **Before pre-mortem** — there is a concrete plan, diff, or change to react to. If the problem is still fuzzy, diagnose first; reasoning about failure modes for the wrong problem wastes the exercise.
- **After pre-mortem** — a recommendation: ship as-is, harden first, or split the change.
- **Neither** is needed for trivial edits where the discipline becomes theater.

If a plan was just approved and the change touches shared state, the pre-mortem is the natural next step. If the user has not yet nailed down what is actually changing, suggest nailing that down first — diagnosing the wrong problem is a more expensive failure mode than any this skill catches.

## Required output

Produce exactly these sections, in this order.

### 1. The change in one sentence

State what is being shipped, in plain language, in a single sentence. If you cannot summarize it in one sentence, the change is too big to reason about — recommend splitting before continuing.

### 2. Failure modes (3-5)

For each mode, write:

- **Scenario** — a concrete sentence describing how the failure happens. Not "could break under load" but "if two Stripe webhooks arrive within 200ms for the same user, both insert a subscription row before either commits the `stripe_id`, leaving a duplicate".
- **Likelihood** — High / Medium / Low, with a one-line justification grounded in this codebase or these users. "Low because we have fewer than 10 paying customers today" is fine if it is true. "Low because we are careful" is not.
- **Blast radius** — what breaks and for whom. "Customer is double-charged" is different from "internal admin dashboard shows wrong count". Quantify when possible (rows, users, dollars, requests).
- **Mitigation** — the smallest concrete change that prevents this scenario. A unique index, a feature flag, a dry-run mode, an idempotency key, a rollback step, a test that would have caught it. If the mitigation reads as "be careful" or "review thoroughly", it is not a mitigation — keep thinking.

Order modes by **likelihood × blast radius**, highest first. If you have fewer than three credible failure modes for a non-trivial change, you are likely anchored on the happy path — re-read the diff with the question "what is this change implicitly assuming?". Common implicit assumptions worth challenging: units, time zones, ordering of writes, idempotency, what happens on retry, what happens if the user closes the tab mid-flow, what the prior state of the database is.

### 3. Recommendation

Pick exactly one. Do not hedge.

- **Ship as-is.** All failure modes are Low likelihood AND Low blast, or already mitigated by the existing plan.
- **Harden first.** One or more mitigations from section 2 must fold into the change before merge. List which ones, by number.
- **Split the change.** The diff is doing too much for the failure surface to be reasoned about. Propose a smaller first slice that ships value with a smaller blast radius, and what gets deferred.

A "maybe ship" recommendation is not allowed. The point of the skill is to force a decision while the cost of changing direction is still low.

## Style notes

Pre-mortem is a thinking exercise, not a checklist ritual. Two real, specific failure modes beat five generic ones. If you find yourself writing "could be slow" or "might have edge cases", delete it and try again with concrete actors, timings, and rows.

Calibrate likelihood against this codebase and these users, not against worst-case theoretical concerns. A race condition in a once-a-quarter cron job is not the same risk as a race condition in checkout, even if the mechanism is identical.

## When not to use this skill

- One-line edits, copy changes, import tweaks, type fixes. Pre-mortem on a typo is comedy.
- Pure refactors with full test coverage where behavior is provably unchanged — the tests are the pre-mortem.
- Greenfield prototypes where the goal is to learn, not to ship safely. Pre-mortem during exploration kills momentum.

If unsure whether the change warrants this discipline, ask: "would I want to be paged at 3am about this?". If yes, do the pre-mortem. If no, ship.
