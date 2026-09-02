# Flitt Skill Guide

This is the main AI-facing guide for Flitt payment integration tasks. Keep answers source-backed, concise, and explicit about uncertainty.

## Source Priority

1. Use `source_md/` as the primary source of truth.
2. Use `source/SOURCE_MD_INDEX.md` and `source/SOURCE_MAP.json` to find relevant local documentation.
3. Use `source/REPOSITORY_INDEX.json` for public GitHub repository metadata and SDK/package discovery.
4. If local docs and GitHub metadata conflict, prefer `source_md/` unless the user provides newer authoritative Flitt material.

Do not crawl Flitt web docs from an AI session. Do not invent Flitt endpoints, request fields, response fields, statuses, SDK behavior, callback behavior, or security rules.

## Safe Coding Rules

- Use placeholders such as `FLITT_MERCHANT_ID`, `FLITT_PAYMENT_SECRET`, and `FLITT_TEST_ORDER_ID`.
- Use sandbox or test terminology wherever payment execution is discussed.
- Never include live secrets, tokens, cookies, authorization headers, full card data, CVV, or private merchant data in generated code or logs.
- Avoid examples that can accidentally charge a real card.
- For direct card-data handling, warn that PCI DSS scope may increase and require merchant-side compliance review.

## Integration Workflow

1. Identify the desired flow: hosted checkout, embedded checkout, direct API payment, wallet, recurring, subscription, withdrawal, installment, open banking, reversal, capture, report, or callback.
2. Open the relevant prompt in `prompts/`.
3. Use `source/SOURCE_MD_INDEX.md` to find source docs, then read the exact files in `source_md/`.
4. Generate minimal code or review findings with source references.
5. Separate documented facts, assumptions, and questions.
6. Include a test checklist and any missing source gaps.

## Core Flitt Patterns From Local Docs

- JSON API requests use a root `request` object and responses use a root `response` object.
- `response_status` describes API request processing, not the final payment result.
- Payment result handling should use documented fields such as `order_status`.
- Signatures are documented in `source_md/docs/api/building-signature.md`.
- Callback handling is documented in `source_md/docs/api/callbacks.md`.
- Test data is documented in `source_md/docs/api/testing.md`; use only safe test placeholders unless the user explicitly asks for documented test values.

## Debugging Workflow

- Redact secrets and unnecessary PII first.
- Identify the request type, endpoint, timestamp, order ID alias, payment ID alias, status fields, and error code.
- Check request shape, signature construction, UTF-8 handling, empty parameters, numeric zero handling, callback signature validation, and final `order_status`.
- Compare evidence against local docs and say when a cause is only a hypothesis.

## Expected Answer Style

For integration answers, include:

- chosen Flitt flow and why it fits the stated use case;
- source files used;
- minimal implementation or review findings;
- safety notes for credentials, logging, and PCI DSS where relevant;
- test checklist;
- unknowns or source gaps.

For undocumented behavior, say it is not documented in the bundled sources and ask the user for authoritative Flitt material or recommend verifying with Flitt support or sandbox tests.
