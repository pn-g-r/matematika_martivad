# Flitt Android SDK Java Example

    ## What This Demonstrates

    This directory provides source-backed guidance for a Flitt Android SDK Java integration example.

    ## Executable Code

    README-only guidance. Use public android-sdk metadata.

    ## Source Support

    Check these local sources before adding or changing code:

    - `source/REPOSITORY_INDEX.json: android-sdk`
    - `source_md/docs/getting-started/mobile.md`\
    - `source_md/docs/api/create-order.md`

    ## Placeholder Credentials

    Use placeholders such as `FLITT_MERCHANT_ID`, `FLITT_PAYMENT_SECRET`, `FLITT_RESPONSE_URL`, and `FLITT_SERVER_CALLBACK_URL`. Do not commit live credentials or local environment files.

    ## Safety

    Do not log secrets, authorization headers, cookies, full card data, CVV, or private customer/merchant data. Use sandbox or test mode first and verify final behavior against the bundled documentation.

	## Recomendation

	Order creation on backend with `POST /api/checkout/token` is preffered other than `POST /api/checkout/url` or `POST /api/checkout/redirect`. Use `checkout_token` to proceed with payment in mobile app.

