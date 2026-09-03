---
name: oklahoma-product-judge
description: Evaluate and shape meaningful product, interface, navigation, and analytical-feature changes for Oklahoma. Use when planning, prioritizing, scoping, or reviewing user-facing changes; do not use for routine data refreshes, mechanical maintenance, or narrow bug fixes that do not alter the user experience.
---

# Oklahoma Product Judge

## Purpose

Help Oklahoma become a more useful phone-first tool for comparing the S&P 500, understanding what drives each result, and building a focused watchlist.

Treat the current product as approximately 51% of the intended experience. Its foundations and identity are deliberate, but substantial polish may still be valuable. Preserve what works without treating the present implementation as the target.

## Product identity

Favor:

- fast cross-sectional comparison;
- clear movement from the market or sector view to an individual name;
- a dense, restrained brokerage-style interface that remains easy to scan;
- progressive detail instead of placing every available fact on the main screen;
- plain explanations of metrics, limitations, and data freshness;
- watchlist decisions that account for concentration and overlapping exposures when the available data supports it.

Do not assume that more metrics, controls, screens, or visual decoration make the product better. A rank or metric is evidence for further judgment, not a prediction or recommendation.

## Evaluate the current experience

Ground the judgment in the repository and, for interface questions, the rendered app when practical. Separate:

- observed behavior;
- reasonable inference;
- design or product preference;
- anything that could not be verified.

Understand the user goal before judging the proposed solution. A user suggestion expresses desired direction; it is not an instruction to force a risky or counterproductive implementation.

## Judge the change

Consider the questions that materially affect the decision:

- Does it help the user compare names, understand a result, or build a better watchlist?
- Does it make the next useful action clearer or faster?
- Does it improve hierarchy and comprehension without hiding important qualifications?
- Does it remove duplication or merely rearrange it?
- Does it fit the existing product identity, or would it quietly become a redesign?
- Is its complexity proportional to its likely user value?
- Could a smaller change capture most of the benefit?
- What existing behavior might regress or become harder to understand?

Use judgment rather than mechanically answering every question.

## Choose a disposition

Recommend one of four outcomes:

- **Proceed**: the change is useful, coherent, and reasonably scoped.
- **Refine**: the goal is sound, but the proposed form should be simplified or adjusted.
- **Assess first**: evidence, feasibility, or user behavior is too uncertain for responsible implementation.
- **Do not recommend**: the change adds more cost, confusion, or risk than value.

Explain the decisive reason briefly. When a smaller alternative is stronger, state it concretely. Do not manufacture objections merely to appear critical.

## Scope and authority

A request to evaluate, review, prioritize, or plan does not authorize implementation. When implementation is explicitly requested, preserve the approved outcome while choosing the safest proportionate approach; stop at assessment or propose an alternative when the repository, data, or architecture makes the requested approach impractical.

Do not silently alter calculation definitions, universe membership, data provenance, update behavior, security boundaries, or deployment architecture as part of product polish. Surface those as separate decisions when they materially affect the proposal.

## Report the judgment

Lead with the recommendation, then give only the reasoning, tradeoffs, uncertainties, and next step needed for the user to decide. Keep straightforward judgments short. For larger proposals, distinguish the desired outcome from optional implementation ideas so the coding agent retains appropriate autonomy.

## Boundaries

This skill supplies product judgment. It does not replace calculation validation, browser-based regression testing, architecture-specific safety checks, investment research, or user-manual creation. Invoke those workflows separately when the task genuinely requires them.
