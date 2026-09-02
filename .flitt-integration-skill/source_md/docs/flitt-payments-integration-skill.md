---
title: Flitt payments integration skill
description: Developer instructions for integrating Flitt payments in Georgia, Uzbekistan, Armenia, and Moldova.
---

# Flitt payments integration skill

Use this skill when you are planning, implementing, reviewing, or testing a Flitt
payments integration for merchants in Georgia, Uzbekistan, Armenia, or Moldova.
It summarizes the Flitt documentation in this site and tells developers and AI
assistants which source pages to read before changing code.

## How to use this skill

1. Read this file first to choose the integration path and regional settings.
2. Read the linked Flitt source pages for the exact request, response, and
   signature details before writing production code.
3. Build the integration in test mode with the Flitt test merchant credentials.
4. Verify callback signature handling and order status handling before enabling
   live traffic.
5. Keep this file attached or open as context when working in an IDE or AI chat.

For AI-assisted work, paste or attach this file together with the relevant local
Flitt docs pages. Flitt does not currently provide an MCP server, so do not
configure or recommend MCP tools, Flitt AI plugins, or AI tool connectors for
this workflow. Use the documentation as explicit context instead.

## Supported merchant countries and currencies

Flitt serves merchants in Georgia, Uzbekistan, Moldova, Armenia, and Kazakhstan.
For this skill, focus on:

| Merchant country | Currency |
| --- | --- |
| Georgia | `GEL`, `USD`, `EUR` |
| Uzbekistan | `UZS` |
| Armenia | `AMD` |
| Moldova | `MDL` |

Customers can pay with Visa and Mastercard cards issued in supported issuing
countries. The local and regional card/payment coverage documented by Flitt also
includes Visa, Mastercard, Maestro, Humo, and UzCard under the `card` payment
system. For Uzbekistan Payme payments, use the Pay by Payme flow described
below.

Read:

- [Supported countries](supported-countries.md)
- [Currencies](api/currencies.md)
- [Supported payment systems](supported-payment-systems.md)

## Choose the integration type

Prefer hosted or embedded checkout unless there is a clear reason to collect
card data directly.

| Use case | Recommended Flitt flow | Main endpoint |
| --- | --- | --- |
| Fast web checkout with lowest PCI scope | Hosted checkout URL | `POST /api/checkout/url` |
| Browser form redirect to Flitt | Hosted checkout redirect | `POST /api/checkout/redirect` |
| Custom web or mobile UI with Flitt token | Embedded checkout | `POST /api/checkout/token` |
| Merchant collects raw card data | Direct integration | Direct API endpoints |
| Saved card or recurring charge | Payment with saved card | Recurring order API |
| Uzbekistan Payme | Redirect or embedded Pay by Payme | `POST /api/checkout/url` or `POST /api/checkout/token` |

Direct integration requires PCI DSS SAQ D because the merchant collects and
transmits card data. Hosted checkout and embedded checkout are usually safer
defaults for new teams.

Read:

- [Payment flow](api/payment-flow.md)
- [Create order](api/create-order.md)
- [Redirect](getting-started/redirect.md)
- [Embedded](getting-started/embedded.md)
- [Direct](getting-started/direct.md)
- [PCI DSS compliance](pcidss-compliance.md)

## Required request rules

All API calls must use HTTPS and `POST`. JSON requests must wrap parameters in
the root `request` object. JSON responses use the root `response` object.

Minimum create-order fields for a normal hosted or embedded payment:

- `order_id`: merchant-generated order ID.
- `merchant_id`: Flitt merchant ID.
- `order_desc`: UTF-8 order description.
- `amount`: integer amount without a decimal separator. For example, `1020`
  means 10.20 in a two-decimal currency such as `GEL`.
- `currency`: regional currency such as `GEL`, `UZS`, `AMD`, or `MDL`.
- `signature`: SHA1 signature generated from the payment secret key and request
  parameters.
- `server_callback_url`: strongly recommended for final server-to-server
  payment result handling.
- `response_url`: recommended for returning the customer to the merchant UI.

Do not treat `response_status` as the payment result. It is the API request
processing status. Use `order_status` for the payment result.

Important order statuses:

- `created`: order exists, but customer has not entered payment details.
- `processing`: payment is still being processed.
- `approved`: payment completed successfully.
- `declined`: payment was declined by Flitt, a bank, or another payment system.
- `expired`: order lifetime expired.
- `reversed`: an approved transaction was fully reversed.

Read:

- [Request structure](api/request.md)
- [Order parameters](api/order-parameters.md)
- [Order status](api/order-status.md)
- [Response codes](api/response-codes.md)

## Signature implementation rules

Every production integration must implement both request signing and response
signature validation.

Signature rules:

- Use the merchant payment secret key as the first item in the signature string.
- Exclude `signature` from the signed fields.
- Exclude `response_signature_string` from response validation.
- Remove absent, empty, or `null` parameters from the signed string.
- Sort remaining parameters alphabetically by key.
- Concatenate values with `|`.
- Apply SHA1 and compare the lowercase hexadecimal digest.
- Preserve UTF-8 values exactly.
- Do not accidentally drop numeric zero values.

In test mode, Flitt can return `response_signature_string`, which helps debug
signature mismatches. Never expose live secret keys in logs.

Read:

- [Signature](api/building-signature.md)
- [Callbacks](api/callbacks.md)
- [Testing](api/testing.md)

## Callback and fulfillment rules

Fulfill orders from the server callback, not only from the browser redirect.
The browser redirect can be interrupted by the customer or network conditions.

Callback requirements:

- Accept `POST` requests at `server_callback_url`.
- Allow Flitt callback IPs documented in the callback page:
  `54.154.216.60` and `3.75.125.89`.
- Return HTTP `200 OK` only after the callback is parsed, signature-verified,
  and safely recorded.
- Expect retries after non-200 responses at these intervals: 2, 60, 300, 600,
  3600, and 86400 seconds.
- Do not depend on redirects from the callback endpoint. Flitt does not follow
  callback redirects.
- Make callback processing idempotent by `order_id` and `payment_id`.

After a verified callback, use `order_status` to decide fulfillment. Ship or
grant service only after `approved`, unless your business process explicitly
handles another status.

Read:

- [Callbacks](api/callbacks.md)
- [Order status](api/order-status.md)

## Uzbekistan Pay by Payme

Use Pay by Payme for Uzbekistan-specific Payme payments. Payme is supported
through redirect or embedded checkout, not direct integration.

Required create-order fields for Pay by Payme:

- `currency: "UZS"`
- `payment_systems: "paybypayme"`
- `payment_method: "paybypayme"`

Flow:

1. Create a payment token or checkout URL from the backend.
2. Redirect the customer to the checkout URL, load it in an iframe, or use the
   embedded checkout flow with the returned token.
3. Let the customer complete strong customer authentication in Payme.
4. Verify the server callback signature.
5. Fulfill only after a verified `approved` order status.

Read:

- [Pay by Payme introduction](api/paybypayme_intro.md)
- [Pay by Payme create order](api/paybypayme.md)

## Testing checklist

Use Flitt test mode before live launch.

Test merchant values:

- `merchant_id`: `1549901`
- Purchase secret key: `test`
- Payout secret key: `testcredit`

Minimum test scenarios:

- Hosted checkout URL returns `checkout_url`.
- Embedded checkout returns `token`.
- Approved Visa and Mastercard card payments.
- Declined Visa and Mastercard card payments.
- 3DS challenge, frictionless, and non-3DS paths.
- Humo and UzCard test cards for Uzbekistan card coverage.
- Pay by Payme with `UZS` and required Payme parameters.
- Callback signature validation.
- Callback retry/idempotency behavior.
- Order status polling for interrupted customer redirects.
- Response code handling for validation errors and declines.

Read:

- [Testing](api/testing.md)
- [Response codes](api/response-codes.md)

## SDK and platform guidance

Use official SDKs where they fit the application stack, but keep signature
validation and callback fulfillment on your backend.

Supported docs in this site include:

- Backend SDKs: Python, PHP, Node.js, C#.
- Frontend SDKs: JavaScript card form and wallet buttons.
- Mobile SDKs and guides: iOS, Android, React Native, and Flutter.
- Wallets: Apple Pay and Google Pay.

Read:

- [About SDK](sdk-and-mobile/sdk/about-sdk.md)
- [Python SDK](sdk-and-mobile/sdk/python.md)
- [PHP SDK](sdk-and-mobile/sdk/php.md)
- [Node.js SDK](sdk-and-mobile/sdk/nodejs.md)
- [C# SDK](sdk-and-mobile/sdk/csharp.md)
- [JavaScript SDK](sdk-and-mobile/sdk/js.md)
- [iOS guide](api/mobile/ios.md)
- [Android guide](api/mobile/android.md)
- [React Native guide](api/mobile/reactnative.md)
- [Flutter guide](api/mobile/flutter.md)

## IDE and AI assistant usage

This skill can be used in major IDEs and AI coding interfaces by opening,
pasting, or attaching this file as project context.

Recommended use in IDEs:

- Visual Studio Code
- Visual Studio
- JetBrains IDEs, including IntelliJ IDEA, WebStorm, PyCharm, PhpStorm, and
  Android Studio
- Xcode
- Eclipse
- NetBeans
- Zed
- Sublime Text
- Vim or Neovim

Recommended use in AI coding/chat GUIs:

- ChatGPT
- Claude
- Gemini
- Microsoft Copilot
- GitHub Copilot Chat
- OpenAI Codex
- Cursor
- Windsurf
- JetBrains AI Assistant
- Continue
- Cline
- Roo Code
- Sourcegraph Cody

Do not look for or recommend a Flitt MCP server, Flitt AI plugin, or AI IDE
connector until Flitt publishes one. Use this Markdown file and the linked
local documentation pages as the source of truth.

## Review checklist for pull requests

Before approving a Flitt integration change, verify:

- The merchant country uses an allowed currency.
- Amounts are sent as integers without a decimal separator.
- Hosted or embedded checkout is used unless direct card collection is required.
- Direct card collection includes PCI DSS SAQ D planning.
- Requests are signed and callbacks are signature-verified.
- `signature` and `response_signature_string` are excluded from signature input.
- Zero values are preserved during signature generation.
- `server_callback_url` is configured and callback handling is idempotent.
- Fulfillment depends on verified `order_status`, not only `response_status`.
- Declines and response codes are handled without creating duplicate orders.
- Test mode covers approval, decline, 3DS, callback, and regional payment paths.
- Pay by Payme uses `UZS`, `payment_systems=paybypayme`, and
  `payment_method=paybypayme`.
