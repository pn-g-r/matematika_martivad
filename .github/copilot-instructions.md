# Flitt Integration Skill managed file

# Flitt Integration Skill

This file enables the Flitt Integration Skill for GitHub Copilot.

Before implementing, reviewing, or debugging Flitt payment code:

- Read `README.md` and `FLITT_SKILL_GUIDE.md` in this skill repository.
- If this file was installed into another project, read `.flitt-integration-skill/README.md` and `.flitt-integration-skill/FLITT_SKILL_GUIDE.md`.
- If `.github/skills/flitt-integration-skill/SKILL.md` is available, use the `flitt-integration-skill` agent skill for Flitt integration tasks.
- `flitt-integration-skill` is an agent skill, not a slash command. Do not use or suggest `/flitt-integration-skill`.
- Use `source_md/` as the primary source of truth and `source/SOURCE_MD_INDEX.md` to find relevant pages.
- Use task prompts from `prompts/` instead of creating tool-specific prompt copies.
- Use only placeholder or sandbox credentials in generated examples.
- Do not invent Flitt endpoints, fields, statuses, SDK behavior, security rules, or payment outcomes.
