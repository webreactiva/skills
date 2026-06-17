<div align="center">

# Web Reactiva Skills

**Agent Skills para programadores de verdad — prácticas, humanas, sin humo.**
Hechas en público por la comunidad de [Web Reactiva](https://webreactiva.com).

[![Ver el catálogo](https://img.shields.io/badge/ver-webreactiva.com%2Fskills-2ea44f)](https://webreactiva.com/skills)

[English](README.md) · **Español**

</div>

> [!NOTE]
> La documentación completa del repo está en inglés. Esto es una versión breve en español.

Colección de [Agent Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
que instalas en Claude Code, OpenCode, Codex, Cursor y muchos otros agentes con un solo comando.
Cada skill es una capacidad enfocada y reutilizable: se la enseñas al agente una vez y no vuelves
a explicarla.

> [!TIP]
> 🛠️ **Usar skills está bien; crear las tuyas es como de verdad se aprende.**
> Aprende a crear tus propias skills, paso a paso, en **[webreactiva.com/guias/crea-skills](https://webreactiva.com/guias/crea-skills)**.

## Instalación

Instala **todas** las skills en el proyecto actual:

```bash
npx skills add webreactiva/skills
```

Instala **una** skill por su nombre:

```bash
npx skills add webreactiva/skills --skill politenizer
```

Añade `-g` para instalarlas en global (`~/.claude/skills`). La distribución usa
[skills.sh](https://skills.sh), compatible con más de 50 agentes.

## Skills

<!-- skills:start -->
| Skill | Qué hace | Página | Instalar |
| --- | --- | --- | --- |
| [`migrate-copilot-instructions`](skills/ai-workflow/migrate-copilot-instructions) | Migrate a project's GitHub Copilot config into Claude Code, Codex, or opencode via a portable AGENTS.md — converting prompts, agents, skills, and MCP, never blind-copying. | [web ↗](https://www.webreactiva.com/skills/migrate-copilot-instructions) | `npx skills add webreactiva/skills --skill migrate-copilot-instructions` |
| [`github-profile-readme`](skills/career/github-profile-readme) | Generate a polished GitHub profile README — the special <owner>/<owner> repo — from real account data, for a person, project, or brand. | [web ↗](https://www.webreactiva.com/skills/github-profile-readme) | `npx skills add webreactiva/skills --skill github-profile-readme` |
| [`politenizer`](skills/career/politenizer) | Turn blunt, angry, or profanity-laden messages into courteous, persuasive ones — in three registers, in the user's own language. | [web ↗](https://www.webreactiva.com/skills/politenizer) | `npx skills add webreactiva/skills --skill politenizer` |
| [`ascii-flow`](skills/engineering/ascii-flow) | Draw portable ASCII / Unicode diagrams — flows, architecture, sequences, trees — that stay aligned and render anywhere with zero tooling, for code comments, READMEs and commit messages. | — | `npx skills add webreactiva/skills --skill ascii-flow` |
| [`git-commit-organizer`](skills/engineering/git-commit-organizer) | Organize pending git changes into clean, atomic Conventional Commits — proposed for your approval, never pushed. | [web ↗](https://www.webreactiva.com/skills/git-commit-organizer) | `npx skills add webreactiva/skills --skill git-commit-organizer` |
<!-- skills:end -->

Catálogo completo y filtrable en **[webreactiva.com/skills](https://webreactiva.com/skills)**.
Para la filosofía, cómo está organizado el repo y cómo contribuir, mira el
**[README en inglés](README.md)** y [`CONTRIBUTING.md`](CONTRIBUTING.md).
