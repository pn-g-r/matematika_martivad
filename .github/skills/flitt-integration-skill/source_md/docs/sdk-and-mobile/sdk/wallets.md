#Create an embedded Apple Pay and Google Pay buttons with JavaScript SDK

Project at GitHub: [https://github.com/flittpayments/js-sdk](https://github.com/flittpayments/js-sdk)

You can place Apple Pay and Google Pay buttons on your website as a regular HTML + JS code.

We developed pre-designed example (HTML/JavaScript) which you can try to use on your site:

## Basic example with both Apple Pay and Google Pay

<p class="codepen" data-height="300" data-default-tab="js,html" data-slug-hash="dPGVGbj" data-pen-title="ApplePay Payment Buttons" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/dPGVGbj">
  ApplePay Payment Buttons</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
<script async src="https://public.codepenassets.com/embed/index.js"></script>

Instead of 
```javascript
<script src='https://cdn.jsdelivr.net/npm/@flittpayments/js-sdk/dist/umd/checkout.js'></script>
<div class='payment-button-container'></div>
```
you can use
```javascript
npm i @flittpayments/js-sdk
import $checkout from "@flittpayments/js-sdk";
```
# Step by step implementation case 

**Step 1**

Create endpoint on your backend which will be called by your frontend application to obtain payment token. 

Endpoint should be integrated as described in instructions at [Merchant embedded checkout page with payment token](https://docs.flitt.com/api/create-order/#merchant-embedded-checkout-page-with-payment-token) 

This is mean, that backend will send [parameters](https://docs.flitt.com/api/order-parameters/#__tabbed_1_1) with POST method to [https://pay.flitt.com/api/checkout/token](https://pay.flitt.com/api/checkout/token) endpoint and obtain token in response.


```json
{
    "response": {
        "token": "07288bca0faaf2dc1870153d31bb7fc0c9f4cc4e",
        "response_status": "success"
    }
}
```

**Step 2**

Obtain payment token from your backend.

**Step 3**

Place your `merchant_id` and `token` values into block:

```
data: {
  merchant_id: 1549901,
  token: "<token obtained from backend>"
}
```

If you need only Apple Pay, set in [JS code](http://localhost:8000/sdk-and-mobile/sdk/wallets/#basic-example-with-both-apple-pay-and-google-pay) parameter

```methods: ["apple"],```

If you need only Google Pay, set in [JS code](http://localhost:8000/sdk-and-mobile/sdk/wallets/#basic-example-with-both-apple-pay-and-google-pay) parameter

```methods: ["google"],```

**Step 4**

Process callback on frontend with `model` object:

```js
  .on("success", function (model) {
    console.log(model);
  })
  .on("error", function (model) {
    console.log(model);
  });
```

**Step 5**

Process callback on your backend (see [parameter](https://docs.flitt.com/api/order-parameters/#__tabbed_1_1) `server_callback_url`). 

Check `orders_status` and `signature` to validate the result.


**Step 6 for (Apple Pay only)**

**Verify your domain in Apple Pay developer account**

- [x] To embedd Apple Pay button from Flitt, you must register all of your web domains where button will be displayed. 
This relates to top-level domains (for example, site.com) and subdomains (for example, shop.site.com, www.site.com), both production and development sites.

- [x] Request Flitt support for `apple-developer-merchantid-domain-association.txt` file.

- [x] When received, place that file at https://example.com/.well-known/apple-developer-merchantid-domain-association where `example.com` is your domain or subdomain.

- [x] Tell Flitt to activate your domain with Apple.
