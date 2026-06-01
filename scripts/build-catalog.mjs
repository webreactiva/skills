#!/usr/bin/env node
/**
 * Build (or check) skills-catalog.json from the skills/ tree.
 *
 * Single source of truth — nothing is typed twice:
 *   - name / description / argument-hint  -> SKILL.md frontmatter (standard agent-skill fields)
 *   - category                            -> parent folder under skills/
 *   - status                              -> top-level folder (work-in-progress => wip, else stable)
 *   - summary / tags / lang / featured    -> hand-authored, kept in skills-catalog.json (by slug)
 *
 * The script refreshes the derived fields and preserves the hand-authored ones.
 * It also refreshes the skills table in README.md between the
 * <!-- skills:start --> and <!-- skills:end --> markers.
 *
 * Usage:
 *   node scripts/build-catalog.mjs           # write skills-catalog.json + README table
 *   node scripts/build-catalog.mjs --check   # fail if anything is missing or out of date (CI)
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS_DIR = join(ROOT, "skills");
const CATALOG_PATH = join(ROOT, "skills-catalog.json");
const README_PATH = join(ROOT, "README.md");

const REPO = "webreactiva/skills";
const BRANCH = "main";
const SITE = "https://webreactiva.com/skills";

// Status derived from the top-level folder a skill lives under.
const STATUS_BY_FOLDER = {
  "work-in-progress": "wip",
  deprecated: "deprecated",
};

// Used only when skills-catalog.json doesn't exist yet. Keep this to categories that
// actually exist — add a new one only when a skill needs it.
const DEFAULT_CATEGORIES = [
  { slug: "career", title: "Career", description: "Your developer brand, communication and growth." },
  { slug: "engineering", title: "Engineering", description: "Version control, code review and day-to-day craft." },
  { slug: "work-in-progress", title: "Work in Progress", description: "Built in public. Rough edges on purpose." },
];

// Hand-authored fields the human owns (kept in skills-catalog.json, copied through
// by slug): summary, tags, lang, featured, and optional status/title overrides.

/** Minimal YAML frontmatter parser: plain, quoted, and folded/literal block scalars. */
function parseFrontmatter(md) {
  const m = md.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return {};
  const lines = m[1].split(/\r?\n/);
  const out = {};
  for (let i = 0; i < lines.length; i++) {
    const km = lines[i].match(/^([A-Za-z0-9_-]+):\s?(.*)$/);
    if (!km) continue;
    const key = km[1];
    let val = km[2] ?? "";
    const isBlock = /^[>|][+-]?$/.test(val.trim());
    if (isBlock || val.trim() === "") {
      const block = [];
      let j = i + 1;
      while (j < lines.length && !/^[A-Za-z0-9_-]+:/.test(lines[j])) {
        if (lines[j].trim() !== "") block.push(lines[j].trim());
        j++;
      }
      val = block.length ? (val.trim().startsWith("|") ? block.join("\n") : block.join(" ")) : "";
      i = j - 1;
    }
    out[key] = val.trim().replace(/^["']|["']$/g, "");
  }
  return out;
}

function listDirs(p) {
  if (!existsSync(p)) return [];
  return readdirSync(p)
    .filter((n) => !n.startsWith(".") && statSync(join(p, n)).isDirectory())
    .sort();
}

function titleCase(slug) {
  return slug
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function scanSkills() {
  const found = [];
  for (const category of listDirs(SKILLS_DIR)) {
    for (const slug of listDirs(join(SKILLS_DIR, category))) {
      const skillMd = join(SKILLS_DIR, category, slug, "SKILL.md");
      if (!existsSync(skillMd)) continue;
      const fm = parseFrontmatter(readFileSync(skillMd, "utf8"));
      found.push({ category, slug, fm, relPath: `skills/${category}/${slug}` });
    }
  }
  return found;
}

function buildCatalog(existing) {
  const handBySlug = new Map((existing.skills || []).map((s) => [s.slug, s]));
  const categories = existing.categories || DEFAULT_CATEGORIES;
  const order = new Map(categories.map((c, i) => [c.slug, i]));
  const problems = [];
  const seen = new Set();

  const skills = scanSkills().map(({ category, slug, fm, relPath }) => {
    if (seen.has(slug)) problems.push(`Duplicate skill slug: "${slug}"`);
    seen.add(slug);
    if (!fm.name || !fm.description)
      problems.push(`${relPath}/SKILL.md is missing "name" or "description" in its frontmatter`);
    if (!order.has(category))
      problems.push(`Unknown category folder "${category}" — add it to "categories" in skills-catalog.json`);

    const hand = handBySlug.get(slug) || {};
    if (!hand.summary) problems.push(`"${slug}": missing hand-authored "summary" in skills-catalog.json`);
    if (!hand.tags || hand.tags.length === 0)
      problems.push(`"${slug}": missing hand-authored "tags" in skills-catalog.json`);

    const status = hand.status || STATUS_BY_FOLDER[category] || "stable";
    const name = fm.name || slug;
    const entry = {
      slug,
      name,
      title: hand.title || titleCase(slug),
      description: fm.description || "",
      summary: hand.summary || "",
      category,
      status,
      tags: hand.tags || [],
      lang: hand.lang || ["en"],
      featured: Boolean(hand.featured),
      path: relPath,
      repoUrl: `https://github.com/${REPO}/tree/${BRANCH}/${relPath}`,
      install: `npx skills add ${REPO} --skill ${name}`,
      canonicalUrl: `${SITE}/${slug}`,
    };
    if (fm["argument-hint"]) entry.argumentHint = fm["argument-hint"];
    return entry;
  });

  // Orphans: a catalog entry whose folder no longer exists.
  for (const s of existing.skills || []) {
    if (!seen.has(s.slug)) problems.push(`Catalog entry "${s.slug}" has no matching skill folder`);
  }

  skills.sort(
    (a, b) => (order.get(a.category) ?? 99) - (order.get(b.category) ?? 99) || a.name.localeCompare(b.name)
  );

  return { catalog: { repo: REPO, site: SITE, categories, skills }, problems };
}

/** Render the README skills tables (one per category, work-in-progress excluded). */
function renderSkillsMarkdown(catalog) {
  const byCat = new Map();
  for (const s of catalog.skills) {
    if (!byCat.has(s.category)) byCat.set(s.category, []);
    byCat.get(s.category).push(s);
  }
  const out = [];
  for (const cat of catalog.categories) {
    if (cat.slug === "work-in-progress") continue;
    const items = byCat.get(cat.slug);
    if (!items || !items.length) continue;
    out.push(`### ${cat.title}`, "", "| Skill | What it does | Install |", "| --- | --- | --- |");
    for (const s of items) {
      out.push(`| [\`${s.name}\`](${s.path}) | ${s.summary} | \`${s.install}\` |`);
    }
    out.push("");
  }
  return out.join("\n").trim();
}

function renderReadme(md, catalog) {
  const start = "<!-- skills:start -->";
  const end = "<!-- skills:end -->";
  const re = new RegExp(`${start}[\\s\\S]*?${end}`);
  if (!re.test(md)) return md;
  return md.replace(re, `${start}\n${renderSkillsMarkdown(catalog)}\n${end}`);
}

function main() {
  const check = process.argv.includes("--check");
  const existing = existsSync(CATALOG_PATH)
    ? JSON.parse(readFileSync(CATALOG_PATH, "utf8"))
    : { categories: DEFAULT_CATEGORIES, skills: [] };

  const { catalog, problems } = buildCatalog(existing);
  const catalogOut = JSON.stringify(catalog, null, 2) + "\n";

  const readmeIn = existsSync(README_PATH) ? readFileSync(README_PATH, "utf8") : null;
  const readmeOut = readmeIn != null ? renderReadme(readmeIn, catalog) : null;

  if (check) {
    const catalogNow = existsSync(CATALOG_PATH) ? readFileSync(CATALOG_PATH, "utf8") : "";
    const catalogDrift = catalogNow !== catalogOut;
    const readmeDrift = readmeIn != null && readmeOut !== readmeIn;
    if (problems.length) console.error("✗ Catalog problems:\n - " + problems.join("\n - "));
    if (catalogDrift) console.error('✗ skills-catalog.json is out of date — run "npm run build:catalog".');
    if (readmeDrift) console.error('✗ README.md skills table is out of date — run "npm run build:catalog".');
    if (problems.length || catalogDrift || readmeDrift) process.exit(1);
    console.log(`✓ Catalog valid and up to date (${catalog.skills.length} skill(s)).`);
    return;
  }

  if (problems.length) console.warn("⚠ Catalog warnings:\n - " + problems.join("\n - "));
  writeFileSync(CATALOG_PATH, catalogOut);
  if (readmeOut != null && readmeOut !== readmeIn) writeFileSync(README_PATH, readmeOut);
  console.log(`✓ Wrote skills-catalog.json (${catalog.skills.length} skill(s)) and refreshed README.`);
}

main();
