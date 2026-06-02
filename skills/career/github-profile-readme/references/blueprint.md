# Profile README blueprint

Two personas, one shared spine: **hero → body → tech → connect**. Adapt freely; these
are scaffolds, not forms to fill.

## Table of contents
- [The shared spine](#the-shared-spine)
- [Persona A — Personal developer profile](#persona-a--personal-developer-profile)
- [Persona B — Project / brand / organization](#persona-b--project--brand--organization)
- [Gold-standard worked example (brand)](#gold-standard-worked-example-brand)

---

## The shared spine

1. **Hero (centered).** `<div align="center">` wrapping: an `#` H1 with name (an emoji
   like 👋 is fine), an `###` tagline that states what they do in one line, a
   one-paragraph value prop, and a row of 3–4 prominent `for-the-badge` CTA badges
   (site, contact, primary work). This is 80% of the impression — make it land.
2. **Body.** A few `##` sections with emoji headers. Persona-specific (below). Keep each
   section short and skimmable; bullets and small tables beat paragraphs.
3. **Tech stack.** A row of `flat` shields.io badges — only tech actually in evidence.
4. **About / Connect.** A short line on who's behind it + a badge row of verified links.
5. **Optional footer.** A one-line `<sub>` sign-off, centered.

Use a `---` rule between the hero and the body, and before the connect block, to give
the page rhythm.

---

## Persona A — Personal developer profile

Voice: first person, concrete, a little personality. Avoid the LinkedIn-robot tone.

Suggested sections (pick what there's real material for — don't force all of them):

- **Hero** — `# Hi, I'm <Name> 👋`, tagline like `### Backend engineer · Go & distributed systems`, one paragraph on what you build and care about, CTA badges (portfolio, blog, email/LinkedIn).
- **🛠️ What I work on / build** — 2–5 bullets of focus areas or signature projects (link the repos).
- **🔭 Currently** — what you're building or learning right now (this is the one bit of the GitHub template worth keeping — but make it specific, not `...`).
- **🧰 Tech I reach for** — stack badges grouped loosely (languages / frameworks / infra).
- **📌 Featured projects** — a small table of pinned repos: name → one-line what+why → link. Use the script's pinned/top-repo data.
- **📫 Connect** — verified social badges (LinkedIn, X, site, email).
- *(Optional)* a GitHub stats widget — see best-practices for the caveats.

Keep it honest: if someone has two repos and a day job, lean on the "currently /
interests / how to reach me" angle rather than inventing a portfolio.

---

## Persona B — Project / brand / organization

Voice: brand voice or third person. Emphasis shifts from "who I am" to "what this is
and where to go". A compact offerings **table** is the workhorse here.

Suggested sections:

- **Hero** — brand name, tagline (the promise in one line), one-paragraph pitch, CTA
  badges (website, primary product/action, main social).
- **A spotlight section or two** — lead with the flagship offering(s), each as its own
  `##` with a few bullets and a `🔗 link → url`.
- **A "What you'll find / What we do" table** — two columns: `emoji **Thing**` | short
  description with inline links. Great for podcasts/newsletters/blogs/communities/products.
- **Work with us / Get involved** — services, hiring, contribution, or join links.
- **🧪 Under the hood** *(optional)* — tech stack badges if the project is itself OSS or
  the audience is technical.
- **Behind the project** — who builds it (link the human), since-when, social badge row.

---

## Gold-standard worked example (brand)

This is the README produced for `webreactiva/webreactiva` and validated as the quality
bar. Note the patterns: centered hero with 4 brand-colored `for-the-badge` CTAs; a
spotlight on the flagship topic; a two-column offerings table with real platform links;
a "work with us" block; a flat tech-badge row; and a centered "behind the project"
block with a verified social row and a `<sub>` sign-off. Brand colors (terracotta
`e56a54`, lilac `9678d3`, mustard `fed757`) are pulled from the project, not invented.

````markdown
<div align="center">

# 👋 Web Reactiva

### Program with AI, surrounded by curious developers — in Spanish, since 2017

**Web Reactiva** is the Spanish-speaking home for developers who want to ship with AI
*without hallucinating*. A podcast with hundreds of episodes, a weekly newsletter, an AI
learning hub, a curated skills catalog for coding agents, and a premium community —
all built to turn what you learn into things you actually build.

[![Website](https://img.shields.io/badge/webreactiva.com-e56a54?style=for-the-badge&logo=googlechrome&logoColor=white)](https://www.webreactiva.com)
[![Newsletter](https://img.shields.io/badge/Newsletter-9678d3?style=for-the-badge&logo=substack&logoColor=white)](https://www.webreactiva.com/newsletter)
[![Podcast](https://img.shields.io/badge/Podcast-fed757?style=for-the-badge&logo=spotify&logoColor=000000)](https://www.webreactiva.com/podcast)
[![X](https://img.shields.io/badge/@webreactiva-000000?style=for-the-badge&logo=x&logoColor=white)](https://twitter.com/webreactiva)

</div>

---

## 🤖 Program with AI

The heart of the project: practical routes to bring AI into your real workflow as a developer.

- **Claude Code** — tricks, workflows and guides
- **AI tools** — hands-on tutorials
- **Skills & plugins** — create and use skills for your agent
- **Coding agents** — compare and master the agents that write code
- **AI models** — benchmarks and comparisons
- **AI & career** — how AI is reshaping your job

🔗 Explore the hub → [webreactiva.com/ia](https://www.webreactiva.com/ia)

## 📚 What you'll find here

| | |
|---|---|
| 🎙️ **Podcast** | Hundreds of episodes on programming with AI, in Spanish — listen at [webreactiva.com/podcast](https://www.webreactiva.com/podcast). |
| 📨 **Newsletter** | The AI newsletter for developers, every Sunday. |
| ✍️ **Blog** | Articles for developers who *make things*. |
| 👥 **Community** | A premium community of curious developers learning to build with AI together. |

## 🤝 Work with us

- **1-on-1 consulting** → [webreactiva.com/consultoria](https://www.webreactiva.com/consultoria)
- **AI for teams** → [webreactiva.com/equipos](https://www.webreactiva.com/equipos)

---

## 🧪 Under the hood

![Next.js](https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwindcss&logoColor=white)

## 🙋 Behind the project

Built by **[Daniel Primo](https://www.linkedin.com/in/danielprimo/)** — developer,
podcaster and educator, helping Spanish-speaking developers grow since **2017**.

<div align="center">

[![Website](https://img.shields.io/badge/Website-e56a54?style=flat&logo=googlechrome&logoColor=white)](https://www.webreactiva.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/danielprimo/)

<sub>Made with ❤ for developers who keep shipping.</sub>

</div>
````
