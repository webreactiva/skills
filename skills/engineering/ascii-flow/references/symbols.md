# Symbol palette & cross-platform compatibility

The available drawing characters, organized by how safely they render across
operating systems, fonts, terminals and editors. Pick the lowest tier that gives
you the look you need — lower tier = more portable.

> **The two failure modes to avoid**
> 1. **Mojibake** — a character the font/encoding can't show, rendered as `?` or `□`.
> 2. **Misalignment** — a character that occupies a different number of columns than
>    you assumed, shifting everything after it. This is the subtle one, caused by
>    *tabs*, *combining marks*, and *East-Asian "ambiguous/wide" width* characters.
> Tiering exists to dodge both.

---

## Tier 1 — Pure ASCII (universal, always safe)

Printable ASCII (U+0020–U+007E). Renders **identically on every OS, every font,
every terminal, every editor, every encoding (ASCII, all Latin code pages,
UTF-8)**. Single-cell width, guaranteed. **Use this for anything embedded in
source code** or that might pass through ASCII-only tooling, plain email, legacy
systems, or be diffed/grepped.

| Purpose            | Characters                | Notes                                  |
|--------------------|---------------------------|----------------------------------------|
| Horizontal line    | `-`  `=`  `_`             | `=` for emphasis/double; `_` for baselines |
| Vertical line      | `\|`                       | the pipe character                     |
| Corners & joints   | `+`                       | one character does every corner/junction |
| Diagonals          | `/`  `\`                  | branches, slopes                       |
| Arrowheads         | `>`  `<`  `^`  `v`        | combine: `-->`  `<--`  `<-->`          |
| Box (full)         | `+`  `-`  `\|`             | `+----+` / `\|    \|` / `+----+`         |
| Dots / fills       | `.`  `:`  `*`  `#`  `o`   | shading, points, emphasis              |
| Labels / brackets  | `[ ]` `( )` `{ }` `' '`   | `.-.`/`'-'` make soft corners          |

Pure-ASCII box and flow:
```
   .--------.        +----------+
   | Client |  --->  |  Server  |
   '--------'        +----+-----+
                          |
                          v
                     +----------+
                     |    DB    |
                     +----------+
```
`.` `'` corners (top `.`, bottom `'`) read softer than `+`; both are 100% portable.

---

## Tier 2 — Unicode box-drawing (recommended for docs/terminal)

The Unicode **Box Drawing** block (U+2500–U+257F) plus **Block Elements**
(U+2580–U+259F). Inherited from IBM CP437/DOS, so coverage is excellent: every
mainstream programming/monospace font ships them (Menlo, SF Mono, Consolas,
Cascadia Code, DejaVu Sans Mono, Source Code Pro, JetBrains Mono, Fira Code…),
and every modern terminal renders them. **All are East-Asian "Narrow" → exactly
one cell wide**, so alignment is stable cross-platform.

**Requirement:** save the file as **UTF-8**. Avoid if the file might be handled by
ASCII-only tooling or shown in a font without these glyphs (rare in 2020s dev
environments, but possible in minimal/embedded contexts).

### Light (the workhorses — use these by default)
```
─  U+2500  horizontal          ┼  U+253C  cross
│  U+2502  vertical            ┌  U+250C  down+right (top-left corner)
├  U+251C  vertical+right      ┐  U+2510  down+left  (top-right corner)
┤  U+2524  vertical+left       └  U+2514  up+right   (bottom-left corner)
┬  U+252C  down+horizontal     ┘  U+2518  up+left    (bottom-right corner)
┴  U+2534  up+horizontal
```

### Rounded corners (softer look)
```
╭  U+256D   ╮  U+256E   ╰  U+2570   ╯  U+256F
```
Slightly less universal than sharp corners in *very* old fonts, but fine in all
current dev fonts. Use sharp corners (`┌┐└┘`) if maximal safety matters.

### Heavy (emphasis / "thick" boxes)
```
━  U+2501   ┃  U+2503   ┏  U+250F   ┓  U+2513   ┗  U+2517   ┛  U+251B
┣  U+2523   ┫  U+252B   ┳  U+2533   ┻  U+253B   ╋  U+254B
```

### Double (strong borders, e.g. an outer frame)
```
═  U+2550   ║  U+2551   ╔  U+2554   ╗  U+2557   ╚  U+255A   ╝  U+255D
╠  U+2560   ╣  U+2563   ╦  U+2566   ╩  U+2569   ╬  U+256C
```

### Dashed / dotted lines (for "optional", "async", "weak" relations)
```
┄ ┅  (light/heavy triple-dash horizontal)   ┆ ┇  (… vertical)
┈ ┉  (light/heavy quadruple-dash horiz.)    ┊ ┋  (… vertical)
╌ ╍  (light/heavy double-dash horizontal)   ╎ ╏  (… vertical)
```

> **Don't mix weights at a joint.** A light `│` won't connect cleanly to a heavy
> `━` or a double `═`. Keep one weight per connected path; you *can* use a
> different weight for a separate element (e.g. double-line outer frame, light
> internals).

---

## Tier 3 — Arrows, blocks, geometry (use sparingly, mind the width)

Expressive, but several carry an **ambiguous-width risk**: under CJK locales or
"East-Asian Wide" font modes they render as **two cells**, shifting the rest of
the row. Safe in Western contexts; risky in mixed/international ones. Mitigate by
placing them at the **end** of a connector, or substitute the ASCII equivalent.

### Arrows
```
SAFE WIDTH (single cell, Box-Drawing-adjacent or block):
  ▶ U+25B6  ◀ U+25C0  ▲ U+25B2  ▼ U+25BC   (black triangles — widely 1-cell)
  ► U+25BA  ◄ U+25C4                        (pointers — used heavily in corpus)

AMBIGUOUS WIDTH (1 cell in Western, 2 in CJK — keep at line ends):
  → U+2192  ← U+2190  ↑ U+2191  ↓ U+2193
  ↔ U+2194  ↕ U+2195  ⇒ U+21D2  ⇐ U+21D0  ⇄ U+21C4
```
ASCII fallback for arrowheads when width safety is paramount: `>` `<` `^` `v`.

### Block elements (bars, fills, progress, shading)
```
█ U+2588 full     ▓ U+2593 dark    ▒ U+2592 medium   ░ U+2591 light shade
▀ U+2580 upper    ▄ U+2584 lower
▌ U+258C left-half  ▐ U+2590 right-half
▏▎▍▌▋▊▉  U+258F..U+2589  (1/8..7/8 left blocks — for fine-grained bar charts)
```
All single-cell and well-supported. Great for gauges, histograms, memory-fill
diagrams.

### Misc symbols
```
• U+2022 bullet    ◦ U+25E6 white bullet   × U+00D7 multiply   · U+00B7 middle dot
° U+00B0 degree    § U+00A7 section        ★ U+2605 / ☆ U+2606 stars
```
These are *ambiguous/variable* width in places — fine as standalone markers, but
don't rely on them inside aligned grids.

---

## Hard rules for alignment (any tier)

- **Never use tabs.** A tab expands to a viewer-defined number of columns;
  it *will* misalign somewhere. Spaces only.
- **No trailing whitespace.** Invisible, pollutes diffs, and gets auto-stripped by
  many editors — shifting your right-hand edges.
- **No combining diacritics or emoji.** Zero-width or double-width; they wreck
  grids.
- **Avoid U+00A0 (no-break space)** as a layout space — it looks like a normal
  space but behaves differently in some tools. Use plain U+0020.
- **One tier of line weight per connected path** (don't join `-`/`─`/`━`/`═`).
- When in doubt about the destination's font/locale, **drop to Tier 1**.

## Quick decision

| Where the diagram lives                          | Recommended tier |
|--------------------------------------------------|------------------|
| Inline in source code (any language)             | **Tier 1** (pure ASCII) |
| README / docs / design doc rendered as UTF-8     | **Tier 2** (box-drawing) |
| Terminal output / TUI                            | **Tier 2**, Tier 3 blocks for bars |
| Email, pastebin, unknown/legacy target           | **Tier 1** |
| International audience / CJK locales possible     | **Tier 1**, or Tier 2 lines + ASCII arrowheads |
