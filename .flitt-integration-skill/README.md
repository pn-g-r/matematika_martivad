# Flitt Integration Skill

Official local AI assistant skill for integrating Flitt payments using Codex, Copilot, Claude Code, Gemini CLI, Cursor, Windsurf, Cline, Roo Code, OpenClaw, and other AI coding tools.

This repository packages local source-backed Flitt documentation, compact indexes, prompts, examples, and short compatibility files so AI coding tools can help with Flitt integrations without crawling web documentation.

## Install

```bash
git clone https://github.com/flittpayments/flitt-integration-skill.git
cd flitt-integration-skill
chmod +x install.sh
./install.sh
```

When run from inside the cloned `flitt-integration-skill` repository, `./install.sh` installs into the parent project directory.

Install into a specific project:

```bash
./install.sh --target /path/to/your/project
```

Install for specific tools:

```bash
./install.sh --target /path/to/your/project --tools codex
./install.sh --target /path/to/your/project --tools copilot
./install.sh --target /path/to/your/project --tools claude
./install.sh --target /path/to/your/project --tools gemini
./install.sh --target /path/to/your/project --tools cursor
./install.sh --target /path/to/your/project --tools windsurf
./install.sh --target /path/to/your/project --tools cline
./install.sh --target /path/to/your/project --tools roo
./install.sh --target /path/to/your/project --tools openclaw
./install.sh --target /path/to/your/project --tools all
```

Dry run:

```bash
./install.sh --target /path/to/your/project --tools all --dry-run
```

`install.sh` installs AI instruction files into the target project.

For Codex it assembles the repository skill package at `.agents/skills/flitt-integration-skill/` with `SKILL.md`, `README.md`, `FLITT_SKILL_GUIDE.md`, `source/`, `source_md/`, `prompts`, and `examples/`.

For GitHub Copilot it installs `.github/copilot-instructions.md` and assembles the discoverable `.github/skills/flitt-integration-skill/` agent skill package with the same local references.

For Claude Code it assembles `.claude/skills/flitt-integration-skill/` with the same local references so the slash command is `/flitt-integration-skill`.

For Gemini CLI it installs `GEMINI.md`.

For OpenClaw it installs the workspace skill file at `skills/flitt-integration-skill/SKILL.md`.

After starting a new session in the target project, `flitt-integration-skill` should appear in the available skills list for tools that support skills. It can copy or symlink files, creates backups before overwriting existing files, keeps project-local access to `source_md`, `prompts`, `examples`, and `FLITT_SKILL_GUIDE.md`, does not modify application source code, and supports dry run mode.

To uninstall generated instruction files safely:

```bash
./uninstall.sh --target /path/to/your/project --tools all --dry-run
./uninstall.sh --target /path/to/your/project --tools all
```

## Usage Examples

Invocation differs by AI tool. Use slash commands only in tools that expose installed skills as slash commands.

Codex CLI:

Codex uses the repository skill package from `.agents/skills/flitt-integration-skill/`. Invoke it by asking in natural language, explicitly mentioning `$flitt-integration-skill`, or selecting it from `/skills`. Do not type `/flitt-integration-skill`; Codex skills are not per-skill slash commands.

```text
> Use flitt-integration-skill to create a Python integration with Flitt hosted checkout.
> $flitt-integration-skill create a Python integration with Flitt hosted checkout.
> Use flitt-integration-skill to review my webhook handler for Flitt signature validation.
> Use flitt-integration-skill to debug this failed Flitt payment using the payload below.
> Use flitt-integration-skill to generate a signature for this Flitt request using documented rules.
```

Claude Code:

Claude Code exposes installed project skills as slash commands from `.claude/skills/<skill-name>/`.

```text
> /flitt-integration-skill create a Node.js Flitt payment integration.
> Use the flitt-integration-skill skill to create a Node.js Flitt payment integration.
> Use Flitt source_md and FLITT_SKILL_GUIDE.md to review this callback handler.
> Create a Flitt Apple Pay integration checklist for this repository.
```

GitHub Copilot Chat:

GitHub Copilot can discover `.github/skills/flitt-integration-skill/`, but Copilot Chat should be invoked with natural language in the target repository. Do not type `/flitt-integration-skill` in Copilot Chat.

```text
@workspace Use flitt-integration-skill to create a PHP Flitt order status checker.
@workspace Use flitt-integration-skill to review this Flitt integration for unsafe logging and signature validation issues.
@workspace Use flitt-integration-skill to generate a Flitt payment flow sequence diagram in Mermaid.
```

Gemini CLI:

Gemini uses repository context and `GEMINI.md`; invoke the skill by asking for it in natural language.

```bash
gemini "Using flitt-integration-skill, create a Python integration with Flitt hosted checkout"
gemini "Review this repository for Flitt webhook validation issues"
gemini "Generate a Flitt Google Pay integration checklist"
```

Cursor:

Cursor uses `.cursor/rules/flitt-integration-skill.mdc`; invoke the skill by asking for it in natural language.

```text
Use the Flitt Integration Skill rules to implement a test Flitt payment flow in Python.
Review this file against the Flitt integration guide and local source_md documentation.
Generate safe placeholder-based Flitt API examples.
```

Windsurf:

Windsurf uses `.windsurf/rules/flitt-integration-skill.md`; invoke the skill by asking for it in natural language.

```text
Use the Flitt integration rules to create a Node.js hosted checkout example.
Use local Flitt source_md to explain required payment parameters.
Review this Flitt callback implementation.
```

Cline / Roo Code:

Cline uses `.clinerules/flitt-integration-skill.md`; Roo uses `.roo/rules/flitt-integration-skill.md`. Invoke the skill by asking for it in natural language.

```text
Use the Cline Flitt Integration Skill rule and guide to implement Flitt hosted checkout.
Use the Flitt source_md docs to create a Postman collection.
Review the current payment integration and report missing signature checks.
```

OpenClaw:

OpenClaw uses the workspace skill root `skills/flitt-integration-skill/SKILL.md`; invoke that skill name if your OpenClaw environment exposes skill commands, otherwise ask for it in natural language.

```bash
openclaw "Use flitt-integration-skill to create Python integration with Flitt"
openclaw "Use flitt-integration-skill to debug this 3DS redirect issue"
openclaw "Use flitt-integration-skill to generate Mermaid sequence diagram"
```

Generic AI CLI:

```text
Use the local Flitt Integration Skill repository at ./flitt-integration-skill.
Read README.md, FLITT_SKILL_GUIDE.md, and source_md.
Create a safe test-only Flitt integration for my stack.
```


## What The Skill Helps With

Use this skill for testing, sending requests, receiving responses, hosted checkout, direct API payments, Apple Pay, Google Pay, withdrawals, installments, open banking, webhooks and callbacks, recurring payments, subscriptions, preauth and capture, reversals, reports, generating signatures, signature validation issues, failed payment debugging, code review, Postman collections, Mermaid diagrams, and SDK or frontend examples where documented.


Copyright (c) Flitt