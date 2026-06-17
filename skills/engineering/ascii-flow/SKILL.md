---
name: ascii-flow
description: >-
  Create clear, well-aligned ASCII / Unicode-art diagrams for software
  architecture, workflows, processes, control flow, state machines, sequence
  diagrams, trees, data structures, memory/bit layouts and tables — the kind
  that live in code comments, READMEs, design docs, commit messages, chat or a
  terminal. Use this skill whenever the user asks to "draw", "sketch", "diagram"
  or "map out" something in plain text or monospace, mentions an "ASCII
  diagram", "text diagram", "diagram in a comment", "box-and-arrow diagram", a
  flowchart/architecture/flow they want as text. Also use it when a rendered
  diagram
  (Mermaid, Graphviz, an image) is not wanted or not possible and the diagram
  must be portable plain text. Prefer this over Mermaid whenever the output has
  to render anywhere with zero tooling.
metadata:
  author: webreactiva.com
  namespace: webreactiva
---

# ASCII Flow — portable text diagrams

Build diagrams out of monospace characters so they render identically in a code
comment, a README, a terminal, a git diff, an email or a chat box — no renderer,
no plugin, no image. The whole value is **portability + alignment**: a diagram
that survives copy-paste everywhere and stays lined up.

This skill is grounded in the taxonomy and ~500 real-world examples catalogued at
[asciidiagrams.github.io](https://asciidiagrams.github.io) (diagrams harvested
from Chromium, the Linux kernel, LLVM, TensorFlow, etc.). The references bundle a
symbol palette, per-family recipes, and a curated gallery.

## When ASCII vs. a real renderer

Use ASCII when the diagram must be **portable plain text**: inline in source code,
in a `.md` that should look right on any host, in a terminal, in a message. Reach
for Mermaid/Graphviz/an image instead when the target renders them and the graph
is large or dense (dozens of nodes, crossing edges) — ASCII gets unreadable past
a certain size. If unsure which the user wants, default to ASCII for anything
that lives near code, and say one line about the tradeoff.

## Step 1 — Pick the visual encoding that fits the content

The single most important decision. Match the shape of the information to the
shape of the diagram. Use this guide:

| The content is…                                              | Use this encoding            | Looks like                              |
|--------------------------------------------------------------|------------------------------|-----------------------------------------|
| A workflow / process / control flow / state machine          | **Directed graph** (top-down) | boxes joined by arrows showing order    |
| System architecture: components and how they relate/connect  | **Undirected graph** / boxes  | boxes joined by plain lines (no arrows) |
| Actors exchanging messages over time (request/response, RPC) | **Sequence**                  | vertical lifelines, horizontal messages |
| A hierarchy / containment / parent-child                     | **Tree**                      | indented branches `├─ └─`               |
| A pipeline / ordered stages / data transformed step by step  | **Linear / sequential**       | `A ──▶ B ──▶ C`                          |
| Tabular data, mappings, register/field descriptions          | **Table**                     | grid of cells with separators           |
| Memory layout, bit fields, nested regions                    | **Nested boxes**              | boxes inside boxes, labelled regions    |
| Coordinates, shapes, a UI mock                                | **Geometry**                  | axes, rectangles, positioned labels     |

State the encoding to yourself before drawing. Picking wrong (e.g. a tree for a
cyclic state machine) is the most common reason a diagram reads badly.

**Orientation:** processes and trees flow **top→bottom**; pipelines and sequences
flow **left→right**. Top-down scales better in narrow columns (code comments);
left-right is natural for short ordered chains.

## Step 2 — Choose a character set (compatibility tier)

The user asked for maximal cross-OS compatibility, so default deliberately. Full
table and the width gotchas are in `references/symbols.md` — the essentials:

- **Tier 1 — Pure ASCII** (` | - + = / \ < > ^ v . ' : * # `). Renders
  **identically on every OS, font, terminal, editor and encoding.** Zero risk of
  misalignment or mojibake. **This is the safe default for code comments** and
  anything that might pass through ASCII-only tooling.
- **Tier 2 — Unicode box-drawing** (`─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ═ ║ ╔ ╗ ╚ ╝ ╭ ╮ ╰ ╯`).
  From the Unicode "Box Drawing" block (CP437 heritage); supported by essentially
  every modern monospace font and terminal, and — critically — **single-cell
  width**, so alignment holds across platforms. Much cleaner lines than ASCII.
  **Best default for READMEs/docs/terminal saved as UTF-8.**
- **Tier 3 — arrows, blocks, geometry** (`→ ↓ ▶ ▼ █ ▌ ░ • ×`). Use sparingly.
  Several of these (notably the simple arrows `→ ← ↑ ↓` and triangles `▲ ▼ ◀ ▶`)
  have **East-Asian *ambiguous* width** — one cell in Western locales, **two cells
  in CJK locales/fonts**, which silently breaks alignment. Keep them at the *end*
  of a connector (where a one-cell shift can't cascade), or prefer ASCII
  arrowheads `> < ^ v`.

**Default rule:** Pure ASCII (Tier 1) for diagrams embedded in source code; Tier 2
box-drawing for standalone docs/terminal output. Don't mix Tier 1 line characters
(`-` `|`) with Tier 2 line characters (`─` `│`) in the same diagram — they have
different stroke weights and joints won't connect. Mention which tier you used.

## Step 3 — Construct on a fixed grid (this is what keeps it aligned)

ASCII art is a grid: every line is a row, every character is a column. Alignment
is the whole game. Discipline:

1. **Spaces only, never tabs.** A tab is rendered as a variable number of columns
   depending on the viewer, so tabs guarantee misalignment. (Several flawed
   diagrams in the source corpus use tabs and fall apart — don't.)
2. **Lay out boxes first, connectors second.** Decide box positions and widths,
   then draw the lines between them.
3. **Keep a vertical connector in the exact same column on every row.** A `│` or
   `|` that drifts one column reads as broken. Count columns; don't eyeball.
4. **Pad labels to a consistent box width.** `│ login  │` and `│ verify │` should
   have the same interior width; pad the shorter label with spaces.
5. **One concept per box; keep labels short.** Long text inside boxes forces wide
   boxes and breaks the layout. Put detail in a legend/notes block below.
6. **No trailing whitespace.** It's invisible but pollutes diffs and some editors
   strip it, shifting your art.
7. **Re-read the finished diagram as a grid** and verify: do all verticals line up,
   do arrowheads touch their boxes, are box interiors equal width? Fix drift before
   returning it.

For multi-line work, it helps to draft the box skeleton, confirm column positions,
then add connectors — rather than writing it all in one pass.

### Counting centers — mandatory before drawing any connector

The most common source of broken diagrams is placing connectors by feel instead of
by arithmetic. Before drawing a single `│`, `┬`, `┴`, or `▼`, compute:

```
center_col = left_border_col + floor(total_box_width / 2)
```

For example, a box that starts at column 8 and is 15 characters wide (including
borders) has its center at column `8 + 7 = 15`. Every connector attached to that
box — the `┬` at the bottom, the `▼` pointing into it, the stem between them —
must be in column 15. Write the number down; do not trust your eye.

**Prefer odd total widths.** A box 15 chars wide has an unambiguous center at `+7`.
A 16-char-wide box has no exact integer center — you must pick +7 or +8 and stick
to it. Odd widths eliminate the ambiguity.

### Multi-way splits — determine destination centers first

A branch line like `┌──────┼──────────┐` is the hardest structure to get right.
The wrong order causes misalignment every time:

- **Wrong:** draw the horizontal bar, then place boxes under it.
- **Right:** determine each destination box's left column and width first, compute
  each center column, then draw the horizontal bar so its `│`/`┼` junction points
  land exactly on those columns.

After drawing, trace each branch top-to-bottom and verify three column numbers
match: (1) the junction on the branch line, (2) the `▼` arrowhead, (3) the `┬`
or top-border of the destination box. If any three differ, fix before returning.

When a split has unequal branch widths, the connector boxes shift and the
horizontal bar must stretch asymmetrically — count the offset explicitly rather
than copy-pasting a symmetric template.

## Step 4 — Apply the family recipe

Each encoding has a reusable construction pattern with worked templates in
**`references/patterns.md`** — read it for the family you chose. Quick reference:

**Directed graph / flow (process, control flow, state machine):**
```
        ┌─────────────┐
        │   start     │
        └──────┬──────┘
               │
               ▼
        ┌─────────────┐      no    ┌─────────────┐
        │  valid?     ├───────────▶│   reject    │
        └──────┬──────┘            └─────────────┘
               │ yes
               ▼
        ┌─────────────┐
        │   commit    │
        └─────────────┘
```

**Architecture (components + relationships), pure-ASCII tier:**
```
   +-----------+        +--------------+        +-----------+
   |  Browser  | <----> | API Gateway  | <----> |  Service  |
   +-----------+        +------+-------+        +-----------+
                               |
                               v
                        +--------------+
                        |   Database   |
                        +--------------+
```

**Sequence (actors over time):**
```
   Client                 Server
     │                       │
     │   POST /login         │
     │──────────────────────▶│
     │                       │
     │   200 + token         │
     │◀──────────────────────│
     │                       │
```

**Tree (hierarchy):**
```
   app/
   ├── api/
   │   ├── routes.py
   │   └── auth.py
   └── core/
       └── config.py
```

See `references/patterns.md` for the rest (linear pipelines, tables, nested/memory
layouts, geometry/UI), each with both ASCII and Unicode variants. For inspiration
on a specific style, browse `references/gallery.md` — curated real examples by
category.

## Step 5 — Wrap the output correctly

- In **Markdown / chat**, always put the diagram in a fenced code block so it
  renders monospace:
  ````
  ```
  ...diagram...
  ```
  ````
- In **source code**, indent every line with the file's comment prefix (`// `,
  `# `, ` * ` inside a block comment) and keep the art aligned *after* the prefix.
- Save files containing Tier 2/3 characters as **UTF-8**.
- Add a short **legend or caption** when symbols aren't self-evident (what dashed
  vs. solid means, what `*` marks, single-letter node names, etc.). The best
  real-world diagrams pair the art with one or two sentences of explanation.

## Quality checklist before returning

- [ ] Encoding matches the content (Step 1); orientation is sensible.
- [ ] Character tier is appropriate for where it'll live, and stated.
- [ ] All vertical connectors hold their column; arrowheads touch their targets.
- [ ] Box interiors are equal width; labels padded consistently.
- [ ] Spaces only — no tabs, no trailing whitespace.
- [ ] Wrapped in a fenced block (md/chat) or comment-prefixed (code).
- [ ] A legend/caption explains anything non-obvious.
- [ ] **Every connector column was computed arithmetically** (`left_col + floor(width/2)`), not placed by eye.
- [ ] **For each branch in a split:** junction column = arrowhead column = destination box center column. Traced top-to-bottom and verified.

---

Thank you asciidiagrams.github.io for your inspiration.
