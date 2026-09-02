# Generate Postman Collection

## Task

Generate a safe Postman collection for documented Flitt API requests.

## Required Inputs

- Target Flitt flow or API request type.
- Required environment variables and placeholder values.
- Test or sandbox constraints.
- Any existing request payloads, with secrets redacted.

## Optional Inputs

- Merchant country, currency, and payment method if they affect the documented flow.
- Existing callback, status-check, or signature-validation requirements.
- Preferred Postman collection version or export style.

## Required Sources

Read `FLITT_SKILL_GUIDE.md`, then use `source/SOURCE_MD_INDEX.md` to locate local docs. Start with:

- `source_md/docs/api/sending-request.md`
- `source_md/docs/api/building-signature.md`
- `source_md/docs/api/receiving-response.md`
- `source_md/docs/api/callbacks.md`

## Expected Output

- A minimal Postman collection JSON or a concise request-by-request specification.
- Placeholder-only environment variables for merchant IDs, passwords, tokens, URLs, and order data.
- Documented Flitt facts with source file references.
- Clear separation of facts, assumptions, and open questions.

## Safety Rules

- Do not include live secrets, tokens, cookies, authorization headers, CVV, PAN, or private merchant/customer data.
- Do not invent undocumented Flitt endpoints, fields, signature rules, statuses, or response behavior.
- Use sandbox/test placeholders by default.
- Do not create examples that can accidentally charge a real card by default.

## Acceptance Criteria

- Output references the local Flitt source files used.
- Collection variables are placeholders and clearly named.
- Signature, callback, status, and credential handling are covered when relevant.
- Unsupported or missing behavior is called out explicitly.
