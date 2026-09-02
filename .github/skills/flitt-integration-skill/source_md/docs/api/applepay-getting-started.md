# Apple Pay integration instructions

## Integrations

Apple Pay payments from Flitt are available both for web and mobile.

Apple Pay on web can be integrated with several options:

- with [redirect](/getting-started/redirect/) to Flitt payment page
- with Apple Pay button [embedded](/api/embedded-custom/#example-applepaygooglepay-buttons) into your website
- directly with [Apple Pay API](https://developer.apple.com/documentation/apple_pay_on_the_web/).

Apple Pay in mobile application can be integrated with Flitt SDK depending on the programming language or framework:

- [Objective-C](/api/mobile/ios/)
- [Swift](/api/mobile/ios-swift/)
- [React Native](/api/mobile/apple-reactnative/)
- [Flutter](/api/mobile/apple-flutter/)
- [in web-view with JavaScript](/api/mobile/apple-webview/)

## Steps for mobile

### Create payment

To start accept payments in your mobile application, first you need to create payment in Flitt.

This is usually done on mobile application backend.



Before you start integration of Apple Pay on mobile, you will need to [Register Apple Merchant ID](/api/applepay-getting-started/#register-apple-merchant-id) 
and [Create Apple Pay certificates](/api/applepay-getting-started/#create-new-apple-pay-certificates). 

Follow instructions bellow.

### Register Apple Merchant ID

Register Apple Merchant ID following the instruction [register merchant ID](https://developer.apple.com/documentation/passkit/apple_pay/setting_up_apple_pay_requirements) at Apple Developer site.

Fill out the form with a description and identifier. 
Your description is for your own needs and may be changed in the future (we recommend using the name of your mobile application). 
The identifier must be unique (in all Apple applications, not just yours) and cannot be changed later (although you can always create another). 
We recommend using merchant.flitt.com.{{Your_app_name}}. Keep this value for future reference when developing the application.

Detailed instruction:

- Go to the Dashboard of your account in Apple Developer [https://developer.apple.com/account/#](https://developer.apple.com/account/#)

- Open menu [Identifiers](https://developer.apple.com/account/resources/identifiers/list)

[![Identifiers]][Identifiers]{ width="400" align="left" }

  [Identifiers]: /static/img/applepay/apay1.png

[//]: # (- in menu Identifiers click choose [Merchant IDs]&#40;https://developer.apple.com/account/resources/identifiers/list/merchant&#41;)

[//]: # ()
[//]: # ([![Merchant IDs]][Merchant IDs]{ width="400" align="left" })

[//]: # ()
[//]: # (  [Merchant IDs]: /static/img/applepay/apay2.png)

- click `Identifiers +` to create Merchant ID: [https://developer.apple.com/account/resources/identifiers/add/bundleId](https://developer.apple.com/account/resources/identifiers/add/bundleId)

[![Add]][Add]{ width="400" align="left" }

  [Add]: /static/img/applepay/apay3.png

- in Register a new identifier choose to register `Merchant IDs`

[![Register]][Register]{ width="400" align="left" }

  [Register]: /static/img/applepay/apay4.png

- Fill out Description and Identifier (merchant.flitt.com.{{your_app_bundle_id}}.):

[![Description]][Description]{ width="400" align="left" }

  [Description]: /static/img/applepay/apay6.png

### Create new Apple Pay certificates

You need to add the certificates to your application to encrypt payment data. To do this, follow 3 steps:


  - Use [Keychain Access](https://developer.apple.com/help/account/create-certificates/create-a-certificate-signing-request) on Mac to generate Certificate Signing Request files.
    
    On other platforms you can use **openssl** commands:

    **Apple Merchant Identity Certificate:**

    ```sh
    openssl genrsa -out merchant.key 2048
    openssl req -new -key merchant.key -out merchant.csr
    ```
    
    **Apple Processing Certificate:**
    
    ```sh
    openssl ecparam -out processing.key -name prime256v1 -genkey
    openssl req -new -sha256 -key processing.key -nodes -out processing.csr
    ```


  - Use these CSR files to generate certificates
  
    section **Apple Pay Payment Processing Certificate:**
    
    [![Processing Certificate]][Processing Certificate]{ width="400" align="left" }
    
      [Processing Certificate]: /static/img/applepay/apay7.png
    
    section **Apple Pay Merchant Identity Certificate:**
    
    [![Identity Certificate]][Identity Certificate]{ width="400" align="left" }
    
      [Identity Certificate]: /static/img/applepay/apay8.png
  
  - Download and send obtained certificates to Flitt support.

