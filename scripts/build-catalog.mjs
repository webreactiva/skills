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

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, realpathSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const SKILLS_DIR = join(ROOT, "skills");
const CATALOG_PATH = join(ROOT, "skills-catalog.json");
const README_PATH = join(ROOT, "README.md");
const README_ES_PATH = join(ROOT, "README.es.md");

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
  { slug: "ai-workflow", title: "AI Workflow", description: "Get more out of your coding agents." },
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

export function buildCatalog(existing) {
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
    // webUrl is synced from the website RSS feed (npm run sync:web), not derived from
    // the tree — preserve it across builds so build:catalog/check stay offline.
    if (hand.webUrl) entry.webUrl = hand.webUrl;
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

// Column labels per README language; the table content (links, install) is shared.
const TABLE_LABELS = {
  en: { what: "What it does", page: "Page", install: "Install" },
  es: { what: "Qué hace", page: "Página", install: "Instalar" },
};

/**
 * Render the README skills table. English groups by category; other languages use a
 * single flat table to stay brief. work-in-progress is always excluded.
 */
function renderSkillsMarkdown(catalog, { lang = "en", grouped = true } = {}) {
  const L = TABLE_LABELS[lang] || TABLE_LABELS.en;
  const rendered = catalog.skills.filter((s) => s.category !== "work-in-progress");
  // Show the "Page" column only when at least one published skill has a webUrl
  // (synced from the site). Keeps the table clean before anything is live.
  const hasWeb = rendered.some((s) => s.webUrl);
  const header = hasWeb
    ? `| Skill | ${L.what} | ${L.page} | ${L.install} |`
    : `| Skill | ${L.what} | ${L.install} |`;
  const divider = hasWeb ? "| --- | --- | --- | --- |" : "| --- | --- | --- |";
  const row = (s) => {
    const page = s.webUrl ? `[web ↗](${s.webUrl})` : "—";
    return hasWeb
      ? `| [\`${s.name}\`](${s.path}) | ${s.summary} | ${page} | \`${s.install}\` |`
      : `| [\`${s.name}\`](${s.path}) | ${s.summary} | \`${s.install}\` |`;
  };

  const out = [];
  if (grouped) {
    const byCat = new Map();
    for (const s of rendered) {
      if (!byCat.has(s.category)) byCat.set(s.category, []);
      byCat.get(s.category).push(s);
    }
    for (const cat of catalog.categories) {
      if (cat.slug === "work-in-progress") continue;
      const items = byCat.get(cat.slug);
      if (!items || !items.length) continue;
      out.push(`### ${cat.title}`, "", header, divider);
      for (const s of items) out.push(row(s));
      out.push("");
    }
  } else {
    out.push(header, divider);
    for (const s of rendered) out.push(row(s));
  }
  return out.join("\n").trim();
}

function renderReadme(md, catalog, opts) {
  const start = "<!-- skills:start -->";
  const end = "<!-- skills:end -->";
  const re = new RegExp(`${start}[\\s\\S]*?${end}`);
  if (!re.test(md)) return md;
  return md.replace(re, `${start}\n${renderSkillsMarkdown(catalog, opts)}\n${end}`);
}

// Each generated README: file path + render options. English is the canonical,
// category-grouped one; the Spanish mirror is a brief, flat table.
const READMES = [
  { path: README_PATH, opts: { lang: "en", grouped: true } },
  { path: README_ES_PATH, opts: { lang: "es", grouped: false } },
];

/** Re-render one README's skills block in place; null when the file doesn't exist. */
function renderReadmeFile({ path, opts }, catalog) {
  if (!existsSync(path)) return null;
  const before = readFileSync(path, "utf8");
  return { path, before, after: renderReadme(before, catalog, opts) };
}

export function loadExisting() {
  return existsSync(CATALOG_PATH)
    ? JSON.parse(readFileSync(CATALOG_PATH, "utf8"))
    : { categories: DEFAULT_CATEGORIES, skills: [] };
}

/** Write the catalog JSON and refresh every README's skills table from it. */
export function writeOutputs(catalog) {
  writeFileSync(CATALOG_PATH, JSON.stringify(catalog, null, 2) + "\n");
  for (const r of READMES) {
    const res = renderReadmeFile(r, catalog);
    if (res && res.after !== res.before) writeFileSync(res.path, res.after);
  }
}

function main() {
  const check = process.argv.includes("--check");
  const { catalog, problems } = buildCatalog(loadExisting());

  if (check) {
    const catalogOut = JSON.stringify(catalog, null, 2) + "\n";
    const catalogNow = existsSync(CATALOG_PATH) ? readFileSync(CATALOG_PATH, "utf8") : "";
    const catalogDrift = catalogNow !== catalogOut;
    const readmeDrift = READMES.map((r) => renderReadmeFile(r, catalog))
      .filter(Boolean)
      .filter((res) => res.after !== res.before)
      .map((res) => res.path.replace(ROOT + "/", ""));
    if (problems.length) console.error("✗ Catalog problems:\n - " + problems.join("\n - "));
    if (catalogDrift) console.error('✗ skills-catalog.json is out of date — run "npm run build:catalog".');
    for (const p of readmeDrift)
      console.error(`✗ ${p} skills table is out of date — run "npm run build:catalog".`);
    if (problems.length || catalogDrift || readmeDrift.length) process.exit(1);
    console.log(`✓ Catalog valid and up to date (${catalog.skills.length} skill(s)).`);
    return;
  }

  if (problems.length) console.warn("⚠ Catalog warnings:\n - " + problems.join("\n - "));
  writeOutputs(catalog);
  console.log(`✓ Wrote skills-catalog.json (${catalog.skills.length} skill(s)) and refreshed README.`);
}

// Run the CLI only when invoked directly, so sync-web.mjs can import the helpers above.
const invokedDirectly =
  process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url);
if (invokedDirectly) main();
