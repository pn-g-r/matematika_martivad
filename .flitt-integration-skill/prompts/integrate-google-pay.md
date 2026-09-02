# Integrate Google Pay

    ## Task

    Plan or review Flitt Google Pay integration.

    ## Required Inputs

    - Target application stack or language.
    - Flitt flow or product surface being implemented or reviewed.
    - Relevant code, payload, error, or desired output, with secrets redacted.
    - Test or sandbox constraints.
    - Order creation on backend with `POST /api/checkout/token` is preffered other than `POST /api/checkout/url` or `POST /api/checkout/redirect`. Use `checkout_token` to proceed with payment in mobile app.

    ## Optional Inputs

    - Existing order, callback, or payment status handling design.
    - Relevant logs with credentials, tokens, cookies, full card data, and PII removed.
    - Merchant country, currency, and payment method if they affect the documented flow.

    ## Required Sources

    Read `FLITT_SKILL_GUIDE.md`, then use `source/SOURCE_MD_INDEX.md` to locate local docs. Start with:

    - `source_md/docs/api/googlepay-getting-started.md`
    - `source_md/docs/api/googlepay-web.md`
    - `source_md/docs/api/googlepay-direct.md`

    ## Expected Output

    - Documented Flitt facts with source file references.
    - Minimal implementation, review findings, checklist, collection, or diagram requested by the user.
    - Clear separation of facts, assumptions, and open questions.
    - Safety notes for credentials, logging, test mode, and PCI DSS where relevant.

    ## Safety Rules

    - Do not invent undocumented Flitt behavior.
    - Use placeholder credentials and test terminology.
    - Do not include live secrets, tokens, cookies, authorization headers, CVV, PAN, or private merchant/customer data.
    - Do not create code that can accidentally charge a real card by default.

    ## Acceptance Criteria

    - Output references the local Flitt source files used.
    - Unsupported or missing behavior is called out explicitly.
    - Generated code or instructions are minimal, reviewable, and test-oriented.
    - Signature, callback, status, and credential handling are covered when relevant.
