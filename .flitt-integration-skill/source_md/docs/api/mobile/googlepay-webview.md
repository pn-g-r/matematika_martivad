# Google Pay&trade; purchases in mobile via web-view

You can use **web-view** integration of Google Pay in your mobile application.
**Web-view** integration is actually a replacement of native SDKs with the JavaScript SDK.

## How to integrate

Use [https://codepen.io/flitt/pen/GRVXjKY](https://codepen.io/flitt/pen/GRVXjKY) code as an example.

### Step 1. Create endpoint on your backend

Endpoint will be requested by your frontend to obtain payment `token` value. 
Endpoint should be integrated as described in [instructions](https://docs.flitt.com/api/create-order/#merchant-embedded-checkout-page-with-payment-token). 
It means, that backend will `POST https://pay.flitt.com/api/checkout/token` the order data and obtain `token` value in response

### Step 2. Rewrite function `request()` from [code example](https://codepen.io/flitt/pen/GRVXjKY)

``` javascript
    function request() {
      return new Promise((resolve) =>
        setTimeout(() => resolve("_token"), 300)
      );
    }
```

to obtain payment `token` from your backend.
Here `_token` should be replaced with backend `token` value.

### Step 3. Place your merchant_id and initial amount into `params` block

``` javascript
    const params = {
      merchant_id: 1549901,
      currency: "GEL",
      amount: 100
    };
```

this is required to draw initial Google Pay button

### Step4. Obtain payment token from backend.

As soon as Google Pay button is clicked, `request()` function will be executed to request new `token` from your backend endpoint from Step 1.
Google Pay button will use `token` string returned.

### Step5. Process callback on frontend with receipt object

Analyze `receipt` object to get the payment result. But you should not trust this response, until your backend receives 
callback and validate response `signature`.

### Step6.  Process callback on your backend, specified in `server_callback_url` parameters.

Check `orders_status` and `signature` parameters to validate the result.