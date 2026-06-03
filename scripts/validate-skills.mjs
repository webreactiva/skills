#!/usr/bin/env node
/**
 * Validate every skills/<category>/<slug>/SKILL.md frontmatter before it ships.
 *
 * Why this exists: build-catalog.mjs parses frontmatter with a deliberately
 * lenient regex, so a YAML mistake (e.g. an unquoted value containing ": ")
 * slips through `npm run check` yet breaks skills.sh and other real YAML
 * parsers with "mapping values are not allowed in this context".
 *
 * This is a focused frontmatter linter, NOT a full YAML engine (the repo is
 * zero-dependency on purpose). It catches the failure modes these simple,
 * flat frontmatters can actually hit:
 *   - missing frontmatter / missing required keys (name, description)
 *   - missing metadata.author / metadata.namespace (repo golden rule)
 *   - a plain (unquoted, non-block) scalar containing ": " or ending in ":"
 *     → the exact thing that triggers "mapping values are not allowed"
 *   - an unterminated quoted value
 *   - an unquoted value with " #" (parsed as a comment)
 *
 * Usage:
 *   node scripts/validate-skills.mjs           # exit 1 if any skill is invalid
 */

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS_DIR = join(ROOT, "skills");

/** All SKILL.md paths under skills/, at any depth. */
function findSkillFiles(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    if (name.startsWith(".")) continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...findSkillFiles(p));
    else if (name === "SKILL.md") out.push(p);
  }
  return out;
}

const BLOCK_SCALAR = /^[|>][+-]?\d*$/; // |, >, >-, |+, >2, ...

/**
 * Lint one frontmatter block. Returns an array of human-readable problems.
 * `lineOffset` makes reported line numbers match the original file.
 */
function lintFrontmatter(body, lineOffset) {
  const problems = [];
  const lines = body.split(/\r?\n/);
  const topKeys = new Set();
  const nested = {}; // parentKey -> Set of child keys
  let blockIndent = -1; // > -1 while inside a block scalar's content

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const ln = lineOffset + i + 1;
    if (line.trim() === "") continue;

    const indent = line.length - line.trimStart().length;
    if (blockIndent >= 0) {
      if (indent > blockIndent) continue; // still inside block scalar content
      blockIndent = -1;
    }

    const km = line.match(/^(\s*)([\w-]+):(?:\s+(.*))?$/);
    if (!km) {
      // A continuation line of a plain scalar would also break on ": ".
      if (/:\s/.test(line))
        problems.push(`line ${ln}: unquoted line contains ": " — quote the value or use a >- block`);
      continue;
    }

    const lvl = km[1].length;
    const key = km[2];
    const raw = km[3] ?? "";
    const val = raw.trim();

    if (lvl === 0) topKeys.add(key);
    else if (currentParent) (nested[currentParent] ??= new Set()).add(key);

    // Empty value at top level: a nested mapping follows (e.g. metadata:).
    if (val === "") {
      if (lvl === 0) currentParent = key;
      continue;
    }

    if (BLOCK_SCALAR.test(val)) {
      blockIndent = indent; // following more-indented lines are block content
      continue;
    }

    if (val[0] === '"') {
      if (val.length < 2 || !val.endsWith('"'))
        problems.push(`line ${ln}: "${key}" has an unterminated double-quoted value`);
      continue;
    }
    if (val[0] === "'") {
      if (val.length < 2 || !val.endsWith("'"))
        problems.push(`line ${ln}: "${key}" has an unterminated single-quoted value`);
      continue;
    }

    // Plain scalar: the ": " (or trailing ":") is what YAML rejects.
    if (/:(\s|$)/.test(raw))
      problems.push(
        `line ${ln}: "${key}" has an unquoted value containing ":" — wrap it in quotes or use a >- block`
      );
    if (/\s#/.test(raw))
      problems.push(`line ${ln}: "${key}" value has " #" which YAML reads as a comment — quote it`);
  }

  // Required keys (repo conventions).
  for (const req of ["name", "description"]) {
    if (!topKeys.has(req)) problems.push(`missing required "${req}" in frontmatter`);
  }
  if (!topKeys.has("metadata")) {
    problems.push('missing "metadata" block (author + namespace are required on every skill)');
  } else {
    const kids = nested["metadata"] || new Set();
    for (const req of ["author", "namespace"]) {
      if (!kids.has(req)) problems.push(`metadata is missing "${req}"`);
    }
  }
  return problems;
}

// `currentParent` is module-scoped so the nested-mapping branch above can see it.
let currentParent = null;

function main() {
  if (!existsSync(SKILLS_DIR)) {
    console.error(`✗ No skills/ directory at ${SKILLS_DIR}`);
    process.exit(1);
  }
  const files = findSkillFiles(SKILLS_DIR).sort();
  let bad = 0;
  for (const file of files) {
    currentParent = null;
    const rel = file.replace(ROOT + "/", "");
    const md = readFileSync(file, "utf8");
    const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) {
      console.error(`✗ ${rel}: missing YAML frontmatter (--- ... ---)`);
      bad++;
      continue;
    }
    const problems = lintFrontmatter(m[1], 1);
    if (problems.length) {
      bad++;
      console.error(`✗ ${rel}:\n   - ${problems.join("\n   - ")}`);
    }
  }
  if (bad) {
    console.error(`\n✗ ${bad} skill(s) with invalid frontmatter.`);
    process.exit(1);
  }
  console.log(`✓ ${files.length} skill(s) have valid frontmatter.`);
}

main();
