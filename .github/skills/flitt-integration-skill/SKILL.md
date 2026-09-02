---
name: flitt-integration-skill
description: Use when implementing, reviewing, debugging, testing, or documenting Flitt payment integrations, including hosted checkout, direct API payments, webhooks, callbacks, signatures, Apple Pay, Google Pay, recurring payments, subscriptions, reversals, reports, SDK usage, and failed payment analysis.
license: MIT
---

<!-- Flitt Integration Skill managed file -->

# Flitt Integration Skill

Use this skill for Flitt payment integration work.

This skill is invoked by natural-language Flitt tasks. It is not a slash command; do not use or suggest `/flitt-integration-skill`.

Before implementing, reviewing, or debugging Flitt payment code:

- Read `README.md` and `FLITT_SKILL_GUIDE.md` from this skill directory first.
- Use `source/SOURCE_MD_INDEX.md` and `source/SOURCE_MAP.json` to find relevant local documentation.
- Read the exact source pages in `source_md/` before giving implementation details.
- Use task prompts from `prompts/` for task-specific workflows.
- Use only placeholder or sandbox credentials in generated examples.
- Do not invent Flitt endpoints, fields, statuses, SDK behavior, security rules, payment outcomes, or operational requirements.
- If these files are missing from the skill directory, fall back to `.flitt-integration-skill/README.md`, `.flitt-integration-skill/FLITT_SKILL_GUIDE.md`, `.flitt-integration-skill/source/`, and `.flitt-integration-skill/source_md/`.
