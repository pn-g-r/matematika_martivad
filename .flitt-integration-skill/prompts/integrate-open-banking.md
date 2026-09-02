# Integrate Open Banking

    ## Task

    Plan or review Flitt Open Banking.

    ## Required Inputs

    - Target application stack or language.
    - Flitt flow or product surface being implemented or reviewed.
    - Relevant code, payload, error, or desired output, with secrets redacted.
    - Test or sandbox constraints.

    ## Optional Inputs

    - Existing order, callback, or payment status handling design.
    - Relevant logs with credentials, tokens, cookies, full card data, and PII removed.
    - Merchant country, currency, and payment method if they affect the documented flow.

    ## Required Sources

    Read `FLITT_SKILL_GUIDE.md`, then use `source/SOURCE_MD_INDEX.md` to locate local docs. Start with:

    - `source_md/docs/api/opb_intro.md`
    - `source_md/docs/api/opb.md`

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
