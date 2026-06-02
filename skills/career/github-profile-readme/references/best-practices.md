# Best practices, badge cookbook & repo setup

## Table of contents
- [The anti-generic rules](#the-anti-generic-rules)
- [Badge cookbook (shields.io)](#badge-cookbook-shieldsio)
- [Accessibility & rendering](#accessibility--rendering)
- [Optional dynamic widgets](#optional-dynamic-widgets)
- [Create the profile repo (when it doesn't exist)](#create-the-profile-repo-when-it-doesnt-exist)
- [Publishing the README](#publishing-the-readme)

---

## The anti-generic rules

A profile README fails in predictable ways. Avoid these and you're most of the way there.

- **No template leftovers.** Delete every `I'm currently working on ...` / `Ask me about ...`
  placeholder from GitHub's default. A `...` on a profile reads as abandoned.
- **No invented facts.** Don't claim years of experience, employers, follower counts,
  "10x", or "passionate about cutting-edge technologies" unless it's true and sourced.
  Hollow superlatives are the tell of an AI-written profile. Be specific instead:
  *"I maintain a 2k-star Rust CLI"* beats *"passionate open-source contributor"*.
- **Every link must resolve.** Use only links from the research or from the user. A 404
  in someone's profile is embarrassing. When unsure, leave it out.
- **Lead with substance, not decoration.** The hero's one paragraph should answer "what
  does this person/project actually do?" before any badge wall.
- **Keep it short.** Aim for something readable in well under a minute. A wall of 40 skill
  badges impresses no one; 6–10 meaningful ones do.
- **Match the persona's voice.** First person and a bit of personality for a human;
  brand voice for a project. Don't write a person like a press release.
- **Don't over-emoji.** One per section header is plenty; emoji confetti reads as noise.

## Badge cookbook (shields.io)

Static badges use this URL shape (the `-` separators are literal; URL-encode spaces as
`%20` or `_`):

```
https://img.shields.io/badge/<LABEL>-<COLOR_HEX>?style=<style>&logo=<simpleicon>&logoColor=<color>
```

- `style`: use **`for-the-badge`** for the few hero CTAs (big, uppercase, prominent) and
  **`flat`** for tech-stack and connect rows (compact).
- `<COLOR_HEX>`: a 6-digit hex *without* `#`. Use the brand's real palette when one
  exists; otherwise the logo's brand color.
- `logo`: a [Simple Icons](https://simpleicons.org) slug (e.g. `nextdotjs`, `react`,
  `python`, `linkedin`, `x`, `spotify`, `substack`, `googlechrome`). If a logo doesn't
  exist, omit it rather than guessing.
- `logoColor`: `white` on dark backgrounds, `000000` on light ones (e.g. on mustard).

Make a badge a link by wrapping it in a markdown image-link:

```markdown
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/USER/)
```

Common logo slugs: `github`, `linkedin`, `x`, `bluesky`, `mastodon`, `youtube`,
`twitch`, `discord`, `telegram`, `gmail`, `substack`, `medium`, `devdotto`, `spotify`,
`applepodcasts`, `rss`, `googlechrome`, `nextdotjs`, `react`, `vuedotjs`, `svelte`,
`typescript`, `javascript`, `python`, `go`, `rust`, `node.js` (`nodedotjs`), `docker`,
`kubernetes`, `postgresql`, `tailwindcss`, `vercel`, `aws`.

## Accessibility & rendering

- The text in `![Alt](...)` is the **alt text** — make it the platform name, not blank.
- Centering needs raw HTML: `<div align="center"> ... </div>`. GitHub allows a small
  HTML subset (`div`, `img`, `sub`, `details`, `table`, `picture`). It strips `style`
  attributes and scripts — don't rely on inline CSS.
- Don't encode meaning in color alone (a colorblind visitor should still get it from the
  label/logo).
- GitHub light/dark themes both render the README. Avoid badges that vanish on one theme
  (e.g. a white logo on a near-white badge). For images that must adapt, use
  `<picture>` with `prefers-color-scheme` sources.

## Optional dynamic widgets

These are nice but third-party — they can rate-limit, change, or break. Offer them, note
the caveat, and never make them load-bearing.

- **GitHub stats:** `https://github-readme-stats.vercel.app/api?username=<user>&show_icons=true`
- **Top languages:** `https://github-readme-stats.vercel.app/api/top-langs/?username=<user>`
- **Streak:** `https://streak-stats.demolab.com/?user=<user>`

## Create the profile repo (when it doesn't exist)

The README only shows on the profile from a specific "special" repo.

### Personal account (User)

1. Create a **new public repository** named **exactly** the username — e.g. user
   `octocat` → repo `octocat/octocat`. (Private won't render on the profile.)
2. Tick **"Add a README file"**. GitHub shows a note that this is a ✨ special ✨ repo.
3. The `README.md` now renders at the top of `github.com/<username>`.

CLI, when authenticated as that user:

```bash
gh repo create <username> --public --add-readme
```

### Organization

1. In the org, create a **public** repository named **`.github`**.
2. Add the file at **`profile/README.md`** (note the `profile/` folder).
3. It renders at the top of the org's profile page.

```bash
gh repo create <org>/.github --public
# then add profile/README.md and push
```

If `gh` is authenticated as the owner, offer to create the repo and push the README in
one go. Otherwise, give the click steps above and let them create it, then push.

## Publishing the README

Producing the README is the deliverable — publishing is the user's call. Hand them the
finished markdown (saved to a local file and shown in the reply) and let them drop it
into their profile repo. **Never run a commit or push unless the user explicitly asks.**
If they do ask:

- You decide *where* to work — an empty current directory, a temp dir, or wherever the
  user prefers; just don't clobber a non-empty working tree without asking.
- **Author the commit as the profile owner** (their `git config user.name/email`).
- Pushing changes a **public profile** — confirm first.
- For a personal profile a **clean commit without a co-author trailer** is the usual
  expectation; confirm if unsure.
