#!/usr/bin/env node
/**
 * Sync each skill's published web page URL from the Web Reactiva skills RSS feed.
 *
 * The feed at FEED_URL lists the skills that are live on the site. Each <item> carries
 * the slug (in <guid>) and the canonical page URL (in <link>). We match by slug and
 * store the page URL as `webUrl` on the matching catalog entry, then regenerate the
 * catalog + README via the normal build.
 *
 * This is the ONLY step that touches the network. `build:catalog` and `check` stay
 * offline: `webUrl` lives in skills-catalog.json (committed) and is preserved on every
 * build, so CI never depends on the website being reachable. There is no extra cache
 * file — the catalog is the single source of truth.
 *
 * Usage:
 *   node scripts/sync-web.mjs        # npm run sync:web
 */

import { buildCatalog, writeOutputs, loadExisting } from "./build-catalog.mjs";

const FEED_URL = "https://www.webreactiva.com/skills/rss.xml";
const TIMEOUT_MS = 20000;

/** Extract { slug -> page URL } from the RSS feed: slug is <guid>, URL is <link>. */
function parseFeed(xml) {
  const map = new Map();
  const items = xml.match(/<item\b[\s\S]*?<\/item>/g) || [];
  for (const item of items) {
    const guid = item.match(/<guid[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/guid>/);
    const link = item.match(/<link[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/link>/);
    const slug = guid?.[1]?.trim();
    const url = link?.[1]?.trim();
    if (slug && url) map.set(slug, url);
  }
  return map;
}

async function fetchFeed(url) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      signal: ctrl.signal,
      headers: { "user-agent": "webreactiva-skills-catalog" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
    return await res.text();
  } finally {
    clearTimeout(timer);
  }
}

async function main() {
  let xml;
  try {
    xml = await fetchFeed(FEED_URL);
  } catch (err) {
    console.error(`✗ Could not fetch the feed (${FEED_URL}): ${err.message}`);
    console.error("  Nothing changed — fix the connection and try again.");
    process.exit(1);
  }

  const webBySlug = parseFeed(xml);
  if (webBySlug.size === 0) {
    console.error("✗ The feed returned no items — refusing to wipe webUrl. Nothing changed.");
    process.exit(1);
  }

  const existing = loadExisting();
  const linked = [];
  const unpublished = [];
  for (const skill of existing.skills || []) {
    const url = webBySlug.get(skill.slug);
    if (url) {
      skill.webUrl = url;
      linked.push(skill.slug);
    } else {
      delete skill.webUrl;
      unpublished.push(skill.slug);
    }
  }

  const { catalog, problems } = buildCatalog(existing);
  if (problems.length) console.warn("⚠ Catalog warnings:\n - " + problems.join("\n - "));
  writeOutputs(catalog);

  const known = new Set((existing.skills || []).map((s) => s.slug));
  const onlyOnSite = [...webBySlug.keys()].filter((s) => !known.has(s));

  console.log(`✓ Synced web links from the feed (${webBySlug.size} item(s) live).`);
  console.log(`  Linked: ${linked.join(", ") || "none"}`);
  if (unpublished.length) console.log(`  In repo, not yet on the site: ${unpublished.join(", ")}`);
  if (onlyOnSite.length) console.log(`  On the site, not in this repo: ${onlyOnSite.join(", ")}`);
}

main();
