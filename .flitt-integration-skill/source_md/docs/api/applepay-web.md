# Apple Pay integration instructions for web

Integrating Apple Pay into a website can be done either through:

- [Redirect method](/getting-started/redirect/)
- [simple embedded with Vue.js](/api/embedded-custom/#example-of-apple-pay-and-google-pay-buttons)
- [advanced embedded with JavaScript](/sdk-and-mobile/sdk/wallets/)
- Directly with [Apple Pay API](https://developer.apple.com/documentation/apple_pay_on_the_web/).

Redirect and embedded methods require integration only with Flitt's API or SDK and thus less coding and complexity.

Integrating Apple Pay with Apple Pay API directly requires additional Apple certificates management and encryption/decryption procedures coding. 

Direct method also involves different approaches depending on tokenized Primary Account Number (DPAN) or an encrypted payment container is used during payment flow processing.

## Apple Pay with redirect to Flitt checkout page 

Refer to [create order](/api/create-order/) to create order on your backend or frontend and redirect payer to the checkout page.
Apple Pay button will automatically appear at checkout page.
The payment is processed on Flitt’s secure platform, reducing complex coding and the risk of handling sensitive data.


## Apple Pay button, embedded to merchant website

Embedded method provides a seamless checkout experience without leaving the merchant website, which can increase conversion rate.

Apple Pay can be embedded in two methods.

**Method with vue.js**

Simple: embedded with [Vue.js](/api/embedded-custom/#example-of-apple-pay-and-google-pay-buttons). This is the easiest way which require less code development.

**Example vue.js Apple Pay button:**

<div style="width: 400px">
<p class="codepen" data-height="300" data-theme-id="light" data-default-tab="result" data-slug-hash="PorvvEw" data-pen-title="Flitt -  Apple, Google Pay buttons" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/PorvvEw">
  Flitt -  Apple, Google Pay buttons</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
</div>

**Method with JavaScript**

Refer to [advanced embedded with JavaScript](/sdk-and-mobile/sdk/wallets/) document to get instruction on how to implement it.
This method provide more control on Apple Pay button behavior and is more flexible if you need to implement additional logic during button display and user click.   


**Verify your domain in Apple Pay developer account**

- [x] To embedd Apple Pay button from Flitt, you must register all of your web domains where button will be displayed. 
This relates to top-level domains (for example, site.com) and subdomains (for example, shop.site.com, www.site.com), both production and development sites.

- [x] Request Flitt support for `apple-developer-merchantid-domain-association.txt` file.

- [x] When received, place that file at https://example.com/.well-known/apple-developer-merchantid-domain-association where `example.com` is your domain or subdomain.

- [x] Tell Flitt to activate your domain with Apple.


## Direct integration with Apple Pay API with decrypted card token

1 [Configur Your Apple Pay Environment](https://developer.apple.com/documentation/apple_pay_on_the_web/configuring_your_environment)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.1 Configure Merchant ID and Certificates
   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1.2 Register and Verify Your Domain

2 Integrate [Apple Payment Request API](https://developer.apple.com/documentation/apple_pay_on_the_web/payment_request_api)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.1 Show Apple Pay Buttons on you site. See [Apple reference](https://developer.apple.com/documentation/applepayjs/displaying_apple_pay_buttons)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2.2 [Construct a PaymentRequest](https://webkit.org/blog/8182/introducing-the-payment-request-api-for-apple-pay/) with parameters:

!!! example "configuration example"

    ``` js
    const applePayMethod = {
      supportedMethods: "https://apple.com/apple-pay",
      data: {
          version: 3,
          merchantIdentifier: "merchant.com.example",
          merchantCapabilities: ["supports3DS", "supportsCredit", "supportsDebit"],
          supportedNetworks: ["masterCard", "visa"],
          countryCode: "GE",
      },
    };
    
    ```

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;where `merchant.com.example` is your Apple Merchant ID from step 1.1

3 Acquire a payment session from Apple with [merchant validation](https://developer.apple.com/documentation/apple_pay_on_the_web/apple_pay_js_api/providing_merchant_validation) process.
This should be done on your backend as oposit to all other steps, done on frontend.

4 Handle Payment Authorization

5 Obtain PaymentResponse and related [ApplePayPayment](https://developer.apple.com/documentation/apple_pay_on_the_web/applepaypayment) dictionary

6 Extract [token](https://developer.apple.com/documentation/passkit_apple_pay_and_wallet/pkpayment/1619239-token) from ApplePayPayment

7 Decrypt [paymentData](https://developer.apple.com/documentation/passkit_apple_pay_and_wallet/apple_pay/payment_token_format_reference)

After decryption the result format should be as follows:

``` json
{
  "applicationPrimaryAccountNumber": "",
  "applicationExpirationDate": "",
  "currencyCode": "",
  "transactionAmount": ,
  "deviceManufacturerIdentifier": "",
  "paymentDataType": "",
  "paymentData": {
    "onlinePaymentCryptogram": ""
  }
}
```

8 Send parameters to Flitt [Payment (direct)](/api/order-parameters-direct/) request

Apple Pay parameter `applicationPrimaryAccountNumber` as Flitt `card_number`

Apple Pay parameter `applicationExpirationDate` as Flitt `expiry_date`

Apple Pay parameter `onlinePaymentCryptogram` as Flitt `cavv`

and additionally Flitt parameter `wallet` = `applepay`

!!! example "Example Apple Pay request to Flitt"

    ``` json hl_lines="12 13 14 15"
    {
      "request": {
        "order_id": "Order_id123",
        "merchant_id": 1549901,
        "order_desc": "Apple Pay Payment with card token",
        "amount": 1000,
        "currency": "GEL",
        "client_ip": "2.2.2.2",
        "server_callback_url": "https://server.com/callback",
        "preauth": "Y",
        "version": "1.0.1",
        "card_number": "4444555566661111",
        "expiry_date": "0527",
        "cavv": "AEBBjhMvE4xRAg97n9DpAoABFA==",
        "wallet": "applepay"
        "signature": "64d565cdf9bfb2ad556eac54bd57706e5dc6c412",
      }
    }
    ```

[//]: # (## Recurring payments with Apple Pay)


[//]: # (## Direct integration with Apple Pay API using JavaScript without cryptografy on backend &#40;with encrypted container&#41;)

[//]: # ()
[//]: # (Register Apple Merchant ID following the instruction register merchant ID at Apple Developer site.)

[//]: # ()
[//]: # (Fill out the form with a description and identifier. Your description is for your own needs and may be changed in the future &#40;we recommend using the name of your mobile application&#41;. The identifier must be unique &#40;in all Apple applications, not just yours&#41; and cannot be changed later &#40;although you can always create another&#41;. We recommend using merchant.flitt.com.{{Your_app_name}}. Keep this value for future reference when developing the application.)

[//]: # ()
[//]: # (Detailed instruction:)

[//]: # ()
[//]: # (### Step 1: Apple Merchant ID registration)

[//]: # ()
[//]: # (1.1 Go to the Dashboard of your [Apple developer account]&#40;https://developer.apple.com/account/#&#41;)

[//]: # ()
[//]: # (1.2 Open menu Certificates, Identifiers & Profiles)

[//]: # ()
[//]: # (1.3 In menu Identifiers click + to create Merchant ID: [https://developer.apple.com/account/resources/identifiers/add/bundleId]&#40;https://developer.apple.com/account/resources/identifiers/add/bundleId&#41;)

[//]: # ()
[//]: # (1.4 Fill out Description and Identifier &#40;merchant.flitt.com.{{Your_app_name}}.&#41;:)

[//]: # ()
[//]: # (### Step 2: Create new Apple Pay certificate)

[//]: # ()
[//]: # (You need to add the certificate to your application to encrypt payment data. To do this, follow 3 steps:)

[//]: # ()
[//]: # (2.1 Provide the information necessary for generating the CSR file to the Flitt support team. To do this, please fill in where the sign “?” is placed:)

[//]: # ()
[//]: # (<pre>)

[//]: # (Country Name &#40;2 letter code&#41; [AU]: ?)

[//]: # (State or Province Name &#40;full name&#41; [Some-State]: ?)

[//]: # (Locality Name &#40;eg, city&#41; []: ?)

[//]: # (Organization Name &#40;eg, company&#41; [Internet Widgits Pty Ltd]: ?)

[//]: # (Organizational Unit Name &#40;eg, section&#41; []: ?)

[//]: # (Common Name &#40;e.g. server FQDN or YOUR name&#41; []: ?)

[//]: # (Email Address []: ?)

[//]: # (</pre>)

[//]: # ()
[//]: # (2.2 Obtain 2 CSR files &#40;Certificate Signing Request&#41; from Flitt support team:)

[//]: # ()
[//]: # (Apple Pay Payment Processing Certificate Request)

[//]: # ()
[//]: # (Apple Pay Merchant Identity Certificate Request)

[//]: # ()
[//]: # (2.3 Use these CSR files to generate certificates to complete 1.4)

[//]: # ()
[//]: # (section Apple Pay Payment Processing Certificate:)

[//]: # ()
[//]: # ()
[//]: # (section Apple Pay Merchant Identity Certificate :)

[//]: # ()
[//]: # ()
[//]: # (2.4 Download and send obtained certificates back to Flitt.)

[//]: # ()

