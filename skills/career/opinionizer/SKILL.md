---
name: opinionizer
description: Sharpen a hedged, lukewarm draft into a strong, opinionated take that lands and travels — without manufacturing conviction the author doesn't hold. Use this whenever the user is drafting a tweet, thread, LinkedIn post, newsletter intro, blog opener, or any short public writing and says things like "make this more opinionated", "this is too soft", "sharpen this take", "this sounds wishy-washy", "I want a strong opinion / hot take", "esto suena flojo", "hazlo más contundente", "ponle más filo", or whenever a draft clearly contains a real belief buried under hedges and dangling caveats. Also trigger when the user has a defensible view but writes it so cautiously that it carries no edge. Works in any language and ALWAYS returns the sharpened versions in the same language as the input draft.
metadata:
  author: webreactiva.com
  namespace: webreactiva
---

# Opinionizer

Most people who say "I'm not opinionated enough" already hold the opinion. They wrote it with the handbrake on. The job here is almost never to *invent* a position — it's to **remove the dampers** and let the position the author already holds hit at full force.

So your default assumption: the conviction is there. Find it, strip what's muffling it, and aim it.

## The one rule you don't break

A strong opinion only works if the author actually holds it and can back it. Your job is to sharpen real conviction, never to manufacture it.

That means:

- **Never fabricate a belief the author doesn't have.** If the draft is genuinely neutral ("here are three options, all fine"), don't bolt on fake outrage. Say so, and ask what they actually think before sharpening.
- **Refuse hollow ragebait.** A take that's provocative but empty — contrarian for clicks, picking a fight the author wouldn't defend — is the failure mode, not the goal. It reads as performative and it burns credibility, especially for practitioners whose whole value is that they *do the thing*.
- **Anchor the claim to something real.** The strongest version of an opinion is usually the one with lived experience attached ("I shipped this and X happened"), not the loudest adjective. Prefer evidence to volume.

If you ever feel like you're inventing the conviction rather than uncovering it, stop and check with the author. That hesitation is the signal.

## Workflow

### 1. Locate the actual claim

Read the draft and extract the single sentence the author would defend in an argument. Strip away the setup, the context, the "I think maybe". What is the one thing they're actually asserting? Write it down in plain words. If you can't find one, the draft has no opinion yet — go ask what they believe before doing anything else.

### 2. Diagnose what's muffling it

Name, specifically, what's draining the force. The usual suspects:

- **Hedges** — "I think", "maybe", "kind of", "in general", "it could be argued", "creo que", "quizá", "en general", "puede ser". (Full bilingual lexicon in `references/patterns.md`.)
- **Self-cancellation** — asserting and retracting in the same breath: "I firmly believe X *can be* useful". Believing firmly and "can be" don't belong together.
- **The dangling caveat** — the most common one. A real, interesting tension ("but you have to iterate it") tacked onto the end as an apology, where it softens everything instead of adding edge.
- **No target** — abstract claims with nothing concrete to push against. "Automation tools are overrated" is weak; "Your $30/mo no-code subscription is on borrowed time" has a target.
- **Buried lede** — the spiciest idea sitting in sentence four instead of leading.

Tell the author what you found before you rewrite — the diagnosis teaches them the pattern so they need you less next time.

### 3. Apply the five moves

These are the levers. Most sharpening is some combination of them:

1. **Cut the hedges.** Delete the qualifiers. State it flat. ("X can sometimes help" → "X works.")
2. **Pick a target.** Replace the abstraction with a concrete thing, group, or belief to push against. Edge needs something to cut.
3. **Flip the caveat into the hook.** Take the dangling "but..." and either lead with it or turn it into an accusation. "But you have to iterate it" becomes "The reason you think it failed is you quit on iteration 2." A caveat aimed at the reader stops being an apology and becomes a jab.
4. **Attach the scar.** Wherever the author has lived experience, weld it on. "I believe X" is an opinion; "I shipped X to production and here's what broke" is a position nobody can wave away.
5. **Compress.** Strong opinions are short. One idea, fewest words, no throat-clearing. Cut the wind-up.

### 4. Produce escalating variants

Return **two or three** rewrites at increasing boldness, clearly labeled, so the author picks their own comfort line. Always include the labels and a one-line note on what each trades off:

- **Confident** — hedges gone, claim stated plainly, still collegial. Safe to post anywhere.
- **Sharp** — adds a target and turns the caveat into a hook. This is usually the one that travels.
- **Provocative** — plants a flag and invites the fight. Highest reach, highest risk; only offer it if the author can actually defend it.

Never hand back a single "correct" answer. The author owns where on the dial they sit.

### 5. Quality check before returning

- Is every claim one the author actually holds? (If unsure, flag it.)
- Did you keep the draft's original language? (Spanish draft → Spanish output.)
- Did you preserve the author's voice, or did you flatten it into generic LinkedIn-influencer cadence? Keep their words, their register, their idioms.
- Is it shorter than the original? It almost always should be.
- Would this still be defensible in a reply thread, or is it a claim that collapses the moment someone pushes? If it collapses, it's ragebait — fix it or drop it.

## Output format

Respond in this structure:

```
**The claim underneath:** [the one sentence they're actually asserting]

**What's muffling it:** [2-4 specific diagnoses — hedges, dangling caveat, no target, etc.]

**Confident:** [rewrite]
**Sharp:** [rewrite]
**Provocative:** [rewrite — only if defensible]

[One line: which you'd pick and why, plus any integrity flag.]
```

Keep the diagnosis tight. The author wants the rewrites and the lesson, not an essay.

## Worked example (Spanish input → Spanish output)

**Draft:** "Creo firme en que las skills pueden ser una herramienta productiva y, hechas a medida, sustituyen a cualquier herramienta de automatización que usaras hasta ahora, pero hay que iterarlas hasta conseguir el objetivo."

**The claim underneath:** Una skill a medida sustituye a tus herramientas de automatización de pago.

**What's muffling it:** "creo firme en que… pueden ser" se afirma y se retracta a la vez; "que usaras hasta ahora" diluye el objetivo; el caveat clave ("hay que iterarlas") va colgado al final pidiendo perdón en lugar de pinchar.

**Confident:** "Una skill hecha a medida sustituye a la herramienta de automatización que estés pagando. Encaja en tu proceso, no en el de un SaaS genérico."

**Sharp:** "Tu suscripción no-code de 30 €/mes tiene los días contados. Una skill a medida hace lo mismo y encaja en *tu* proceso. ¿Que probaste y no funcionó? La abandonaste en la iteración 2."

**Provocative:** "Las herramientas no-code son una muleta cara. Una skill a medida las sustituye todas — y si crees que no, es que nunca la iteraste lo suficiente para verlo."

*Pick: Sharp. Lleva objetivo concreto y convierte el caveat en pulla sin afirmar nada que no puedas defender con tu propia práctica.*

## Worked example (English input → English output)

**Draft:** "I think TypeScript is generally a good idea for most projects, though of course it adds some overhead and isn't always necessary for smaller things."

**The claim underneath:** TypeScript is worth the cost on real projects.

**What's muffling it:** "I think… generally… for most" stacks three hedges; "of course it adds overhead" pre-concedes the counterargument; "isn't always necessary" retreats before anyone attacked.

**Confident:** "On any project you'll maintain past next month, TypeScript pays for itself."

**Sharp:** "The 'TypeScript is overhead' crowd is usually shipping code nobody maintains. On anything with a second contributor, the types are the cheap part — the bugs they catch aren't."

*Pick: Sharp if you've actually felt that pain; Confident if you'd rather not pick a fight today.*

## Extended patterns and lexicon

For the full bilingual hedge lexicon (English + Spanish), the extended move catalog, hook templates, and the anti-patterns to avoid (false dichotomy, strawman, manufactured contrarianism), read `references/patterns.md`.
