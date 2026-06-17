# Gallery — curated real-world examples

Hand-picked diagrams from the [asciidiagrams.github.io](https://asciidiagrams.github.io)
corpus (originally from the Chromium, Linux kernel and LLVM source trees). Each is
a proven pattern — study the one closest to your task and adapt it. The "why it
works" note calls out the technique worth copying.

Browse the full ~500-example catalogue at the site, filterable by visual encoding,
scope and concept.

---

## Sequence — request/response between two actors
*Chromium, FedCM (`federated_auth_request_impl`).* Encoding: directed / sequence.
```
//  .-------.                           .---.
//  |Browser|                           |IDP|
//  '-------'                           '---'
//      |                                 |
//      |     GET /fedcm.json             |
//      |-------------------------------->|
//      |                                 |
//      |        JSON{idp_url}            |
//      |<--------------------------------|
//      |                                 |
//      | POST /idp_url with OIDC request |
//      |-------------------------------->|
//      |<--------- token / signin_url ---|
```
**Why it works:** two fixed lifeline columns; pure-ASCII so it's safe inside a
`//` comment; message label sits above its own arrow; soft `.-.`/`'-'` corners on
the actor boxes. Repeats the actor boxes at the bottom in the original for long
sequences (orientation reminder).

---

## State machine — cyclic flow with a return rail
*Linux kernel, TCP BBR.* Encoding: directed graph with cycles.
```
 *             |
 *             V
 *    +---> STARTUP  ----+
 *    |        |         |
 *    |        V         |
 *    |      DRAIN   ----+
 *    |        |         |
 *    |        V         |
 *    +---> PROBE_BW ----+
 *    |      ^    |      |
 *    |      |    |      |
 *    |      +----+      |
 *    |                  |
 *    +---- PROBE_RTT <--+
```
**Why it works:** a left rail (`+--->`) feeds forward edges and a right rail
(`----+`) collects back edges, so nothing crosses. The `^`/`+----+` self-loop on
PROBE_BW is a clean idiom for "stays in this state". All Tier 1.

---

## Tree — annotated hierarchy
*Chromium, frame tree pretty-printer.* Encoding: tree.
```
//        Site A (D pending) -- proxies for B C
//          |--Site B --------- proxies for A C
//          +--Site C --------- proxies for B A
//               |--Site A ---- proxies for B
//               +--Site A ---- proxies for B
//                    +--Site A -- proxies for B
//       Where A = http://127.0.0.1/
//             B = http://foo.com/ (no process)
//             C = http://bar.com/
```
**Why it works:** single-letter node names keep rows short; a legend (`Where A =
…`) carries the detail; dashed run-ons (`---------`) align the right-hand
annotations into a column. Pure ASCII.

---

## Tree — abstract, with dirty-node marks
*Chromium, layout relayout ancestor.* Encoding: tree.
```
//       div [relayout-common-ancestor]
//      /   \
//   *div  *div
//    /      /
// *div   *div
```
**Why it works:** `/` and `\` make a compact binary-tree fork without box-drawing;
a leading `*` marks "dirty" nodes (explained in surrounding prose). Tiny and
readable.

---

## Nested boxes — the CSS box model
*Chromium, layout.* Encoding: geometry / nested.
```
//       |----------------------------------------------------|
//       |                   margin-top                       |
//       |     |-----------------------------------------|    |
//       |     |             border-top                  |    |
//       |     |    |--------------------------|----|    |    |
//       |     |    |       padding-top        |####|    |    |
//       |     |    |    |----------------|    |####|    |    |
//       | ML  | BL | PL |  content box   | PR | SW | BR | MR |
//       |     |    |    |----------------|    |    |    |    |
//       |     |    |      padding-bottom      |    |    |    |
//       |     |    |--------------------------|----|    |    |
//       |     |             border-bottom               |    |
//       |     |-----------------------------------------|    |
//       |                   margin-bottom                    |
//       |----------------------------------------------------|
```
**Why it works:** concentric rectangles with inner walls aligned under outer ones;
a middle label row (`ML | BL | PL | … | MR`) names each band; `####` marks the
scrollbar region. Pure ASCII, perfectly columnar.

---

## Undirected graph — ring topology + data table
*Linux kernel, NUMA scheduler.* Encoding: undirected graph + table.
```
 *   node   0   1   2   3
 *     0:  10  20  30  20
 *     1:  20  10  20  30
 *     2:  30  20  10  20
 *     3:  20  30  20  10
 *
 *   0 ----- 1
 *   |       |
 *   |       |
 *   3 ----- 2
```
**Why it works:** pairs a distance *table* with the *graph* it describes — two
encodings reinforcing one idea. Plain `-----`/`|` edges (no arrowheads) because the
relation is symmetric. (The original uses tabs further down and misaligns — a
reminder to use spaces.)

---

## Inline directed edge — a pointer loop
*Linux kernel, BTF verifier.* Encoding: directed graph (compact).
```
 * BTF_KIND_CONST -> BTF_KIND_PTR -> BTF_KIND_CONST -> BTF_KIND_PTR +
 *                        ^                                         |
 *                        +-----------------------------------------+
```
**Why it works:** shows a cycle inline with a single wrap-around edge (`+`
corners, `^` arrowhead). Great lightweight idiom when a full box diagram is
overkill — the arrow *is* the explanation.

---

## Takeaways to reuse

- **Legends beat long labels.** Name nodes `A`/`B`/`*`, explain below.
- **Pair encodings** when it helps (table + graph, diagram + prose).
- **Pick the rail/lifeline columns first**, then fill — every strong example has a
  rigid column skeleton.
- **Pure ASCII dominates in code comments** because it's safe in any `//`, `#` or
  ` * ` context and any encoding — match that when your diagram lives in source.
