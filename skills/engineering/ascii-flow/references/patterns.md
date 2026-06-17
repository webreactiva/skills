# Diagram family recipes

One reusable construction pattern per visual encoding. Each shows a template; most
show both a **Tier 1 (pure ASCII)** and **Tier 2 (Unicode)** variant so you can
match the target. Read the section for the encoding chosen in Step 1 of SKILL.md.

Contents:
1. Directed graph — workflow / process / control flow
2. State machine (directed graph with cycles)
3. Architecture — components & relationships (undirected)
4. Sequence — actors exchanging messages over time
5. Tree — hierarchy / containment
6. Linear pipeline — ordered stages
7. Table — tabular data, mappings, registers
8. Nested boxes — memory / bit layout / containment
9. Geometry & UI sketches

---

## 1. Directed graph — workflow / process / control flow

Boxes are steps/states; arrows show order. Flow **top→bottom**. A branch is a box
with two outgoing arrows, each labelled with its condition.

Construction order: (a) stack the boxes vertically with equal interior width;
(b) drop a `│`/`|` between them in a fixed column; (c) add `▼`/`v` arrowheads
touching the next box; (d) for branches, send a side connector out a `├`/`+` and
turn it with a corner.

Tier 2:
```
        ┌──────────────┐
        │   receive     │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐   no    ┌──────────────┐
        │   valid?      ├───────▶│   drop        │
        └──────┬───────┘         └──────────────┘
               │ yes
               ▼
        ┌──────────────┐
        │   enqueue     │
        └──────────────┘
```

Tier 1 (same diagram, pure ASCII):
```
        +--------------+
        |   receive    |
        +------+-------+
               |
               v
        +--------------+   no    +--------------+
        |   valid?     +------->|    drop      |
        +------+-------+         +--------------+
               | yes
               v
        +--------------+
        |   enqueue    |
        +--------------+
```

Tips: keep condition labels (`yes`/`no`) right next to the line they annotate.
A fan-out from one box to many uses `┬`/`├`/`┐` to split the line.

---

## 2. State machine (directed graph with cycles)

Like a flow, but states can loop back. Use a left-hand "return rail" so back-edges
don't cross the forward path. (Pattern lifted from the Linux BBR diagram.)
```
            │
            ▼
   ┌──▶ STARTUP  ───┐
   │      │         │
   │      ▼         │
   │    DRAIN   ────┤
   │      │         │
   │      ▼         │
   ├──▶ PROBE_BW ───┤
   │    ▲   │       │
   │    └───┘       │   (self-loop)
   │                │
   └─── PROBE_RTT ◀─┘
```
The vertical rails on the left (incoming) and right (outgoing) collect the
back-edges so arrows never cross. Label transitions in a legend below if the
conditions are complex.

---

## 3. Architecture — components & relationships (undirected)

Components are boxes; relationships are **plain lines** (no arrowheads) unless the
relation has a direction (then add one). Lay out by layer or by tier. Nest boxes
to show containment.

Tier 1 (recommended for code/READMEs — maximally portable):
```
   +-------------+      +----------------+      +-------------+
   |   Browser   | <--> |  API Gateway   | <--> |  Service A  |
   +-------------+      +-------+--------+      +-------------+
                                |
                                |
                         +------+-------+
                         |   Database   |
                         +--------------+
```

Tier 2 with a double-line frame grouping a subsystem:
```
   ╔════════════════════════════════════╗
   ║  edge                              ║
   ║   ┌──────────┐     ┌──────────┐    ║
   ║   │  CDN     │─────│  WAF     │    ║
   ║   └──────────┘     └────┬─────┘    ║
   ╚═════════════════════════│══════════╝
                             │
                       ┌─────┴──────┐
                       │  origin    │
                       └────────────┘
```
Use the double frame (`═ ║ ╔…`) for the *grouping* and light lines (`─ │`) for the
*internals* — different weights distinguish "boundary" from "connection".

---

## 4. Sequence — actors exchanging messages over time

Actors get boxes across the top; a vertical **lifeline** drops from each; messages
are horizontal arrows between lifelines, time flowing downward. Keep lifeline
columns fixed for the whole diagram. (Pattern from Chromium's FedCM diagram.)

```
   ┌────────┐                       ┌─────┐
   │Browser │                       │ IDP │
   └───┬────┘                       └──┬──┘
       │                               │
       │     GET /fedcm.json           │
       │──────────────────────────────▶│
       │                               │
       │        {idp_url}              │
       │◀──────────────────────────────│
       │                               │
       │   POST /idp_url (request)     │
       │──────────────────────────────▶│
       │                               │
       │       token | signin_url      │
       │◀──────────────────────────────│
       │                               │
```
Tier 1 lifelines use `|`, messages use `------>` / `<------`. Right-pointing =
request, left-pointing = response. Put the message label centred above its arrow.

---

## 5. Tree — hierarchy / containment

Parent at top/left; children indented under it. Use `├─` for a middle child, `└─`
for the last child, and `│` to carry the line down past earlier branches. This is
the familiar `tree` / file-explorer style.

Tier 2:
```
   service/
   ├── api/
   │   ├── routes.py
   │   ├── auth.py
   │   └── models.py
   └── core/
       ├── config.py
       └── db.py
```

Tier 1:
```
   service/
   |-- api/
   |   |-- routes.py
   |   |-- auth.py
   |   `-- models.py
   `-- core/
       |-- config.py
       `-- db.py
```
(`` `-- `` for the last child reads as a corner in ASCII.) For abstract trees
(not files), the same shape works with node labels; annotate dirty/changed nodes
with a leading `*` and explain in a legend.

---

## 6. Linear pipeline — ordered stages

Short ordered chains read best **left→right**. One box per stage, arrows between.
```
   ┌────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐
   │ ingest │──▶│ validate │──▶│ transform│──▶│  load  │
   └────────┘   └──────────┘   └──────────┘   └────────┘
```
Tier 1: `[ ingest ] --> [ validate ] --> [ transform ] --> [ load ]`.
If it gets too wide for the column, switch to the top-down directed-graph form.

---

## 7. Table — tabular data, mappings, registers

A grid with a header row separated by a rule. Pad every cell to the column width.

Tier 2 (box-drawing grid):
```
   ┌─────────┬──────────┬───────────────┐
   │ field   │ bits     │ meaning       │
   ├─────────┼──────────┼───────────────┤
   │ opcode  │ 31..26   │ instruction   │
   │ rs      │ 25..21   │ source reg    │
   │ rt      │ 20..16   │ target reg    │
   └─────────┴──────────┴───────────────┘
```

Tier 1 (Markdown-pipe style, also valid as a real MD table):
```
   | field  | bits   | meaning      |
   |--------|--------|--------------|
   | opcode | 31..26 | instruction  |
   | rs     | 25..21 | source reg   |
   | rt     | 20..16 | target reg   |
```
For a register/bit-field strip, see Nested boxes below.

---

## 8. Nested boxes — memory / bit layout / containment

Boxes inside boxes show containment (CSS box model, memory regions, packet
frames). Each region gets a label; align inner walls under outer walls.

Bit-field / register strip (label each field, mark the bit boundaries):
```
    31           26 25     21 20     16 15                  0
   ┌───────────────┬─────────┬─────────┬────────────────────┐
   │     opcode     │   rs    │   rt    │     immediate       │
   └───────────────┴─────────┴─────────┴────────────────────┘
```

Concentric containment (memory/CSS-box style), Tier 1:
```
   +--------------------------------------+
   |  margin                              |
   |   +------------------------------+   |
   |   |  border                      |   |
   |   |   +----------------------+   |   |
   |   |   |  padding             |   |   |
   |   |   |   +--------------+   |   |   |
   |   |   |   |  content     |   |   |   |
   |   |   |   +--------------+   |   |   |
   |   |   +----------------------+   |   |
   |   +------------------------------+   |
   +--------------------------------------+
```

Memory fill / occupancy with block elements (Tier 3 blocks, single-width):
```
   heap: ████████████░░░░░░░░  60% used
```

---

## 9. Geometry & UI sketches

For coordinates, shapes, or a quick UI mock. Use a frame for the viewport, place
labels at their positions, and add axes if coordinates matter.

UI mock:
```
   ┌──────────────────────────────────┐
   │ ☰  My App                  ◯ ◯ ◯ │
   ├──────────────────────────────────┤
   │  ┌────────┐                       │
   │  │ search │   [ Go ]              │
   │  └────────┘                       │
   │                                   │
   │  • item one                       │
   │  • item two                       │
   └──────────────────────────────────┘
```

Coordinate sketch:
```
   y
   ▲
   │      • (3,4)
   │
   │  • (1,2)
   └───────────────▶ x
```
(Remember the ambiguous-width caveat on `▲ ▶` — fine here at the axis ends.)

---

## General reminders (repeat of the alignment discipline)

- Boxes first, connectors second; verify columns by counting, not eyeballing.
- Equal interior width for sibling boxes; pad labels with spaces.
- Don't mix line weights at a joint.
- Spaces only, no tabs, no trailing whitespace.
- Add a legend/caption for anything non-obvious.
