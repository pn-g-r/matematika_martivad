## Mobile SDKS

[//]: # (Flitt SDKs let you natively integrate payment in your mobile application:)

Flitt mobile SDKs provide possibility to embed card payment form and Apple/Google Pay buttons directly into you application.

The main advantages to use Flitt mobile SDKs are:

- you are not required to be a PCI DSS compliant as your application and backend will not access, transmit or store sensitive payment data

- Flitt SDK allows payment methods to be natively embedded in application layout and are easily designed with branded styles and colors

- For Apple and Google Pay Flitt SDK make integration much more simple.  
No need to pass encrypted payloads to your backend.
No need to integrate [Google Pay API](https://developers.google.com/pay/api/android/overview)
and [Apple Pay API](https://developer.apple.com/documentation/passkit_apple_pay_and_wallet/apple_pay) 
and deal with certificates management and decryption. 
SDK will handle all the integration with Apple and Google on its own. 


<div class="grid cards" markdown>

-   __How embedded mobile card form can look like__

    ---
    
    [![Mobile card]][Mobile card]{ width="400" align="left" }
    
      [Mobile card]: /static/img/intro/cards_mobile.png

  
-   __How embedded mobile card form can look like__

    ---
  
    [![Wallets]][Wallets]{ width="400" align="left" }
      
      [Wallets]: /static/img/intro/wallets_mobile.png


</div>

### Steps to integrate mobile SDK

#### Step 1. Create payment token on backend

Use [Merchant embedded checkout page with payment token](/api/create-order/#merchant-embedded-checkout-page-with-payment-token) instructions to create payment and obtain payment `token`.

#### Step 2. Create payment form in mobile application

Use one of Flitt mobile SDKs depending on the framework or programming language your application is developed with:

- [iOS SDK (Objective-C) for cards](/api/mobile/ios/)

- [iOS SDK (Objective-C) for Apple Pay](/api/mobile/apple-ios/)

- [iOS SDK (Swift) for cards](/api/mobile/ios-swift/)

- [iOS SDK (Swift) for Apple Pay](/api/mobile/apple-ios-swift/)

- [React Native for cards](/api/mobile/reactnative/)

- [React Native for Apple Pay](/api/mobile/apple-reactnative/)

- [React Native for Google Pay](/api/mobile/googlepay-reactnative/)

- [Flutter for cards](/api/mobile/flutter/)

- [Flutter for Apple Pay](/api/mobile/apple-flutter/)

- [Flutter for Google Pay](/api/mobile/googlepay-flutter/)

- [Android (Java) for cards](/api/mobile/android/)

- [Android (Java)for Google Pay](/api/mobile/googlepay-android/) 

Refer to example applications in each repository to create card payment form or Apple Pay/Google Pay button

#### Step 3. Pass payment token from _Step 1_ from your backend to mobile application.

Each SDK have method to process payment with token:

- iOS Apple Pay: [`applePayWithToken()`](https://github.com/flittpayments/ios-sdk/blob/master/Cloudipsp/PSCloudipspApi.h#L60)

- iOS with card: [`withToken()`](https://github.com/flittpayments/ios-sdk/blob/master/Cloudipsp/PSCloudipspApi.h#L54C3-L54C12)

- Android (Java) Google Pay: [`googlePayInitialize(final String token...)`](https://github.com/flittpayments/android-sdk/blob/master/library/src/main/java/com/cloudipsp/android/Cloudipsp.java#L136)

- Android (Java) with card: [`payContinue(final String token...)`](https://github.com/flittpayments/android-sdk/blob/master/library/src/main/java/com/cloudipsp/android/Cloudipsp.java#L524)

- React Native Google Pay: [`googlePayToken()`](https://github.com/flittpayments/react-native/blob/2f2ca76c24e2f0e90d4fb90e146dee4b42f4fe02/src/Cloudipsp.ts#L156)

- React Native Apple Pay: [`applePayToken()`](https://github.com/flittpayments/react-native/blob/2f2ca76c24e2f0e90d4fb90e146dee4b42f4fe02/src/Cloudipsp.ts#L94)

- React Native with card: [`payToken()`](https://github.com/flittpayments/react-native/blob/2f2ca76c24e2f0e90d4fb90e146dee4b42f4fe02/src/Cloudipsp.ts#L74)

- Flutter Google Pay: [`googlePayToken()`](https://github.com/flittpayments/flutter/blob/7bc950056d2242d315c349b26ae8319b1c2c9c8f/lib/src/cloudipsp.dart#L237)

- Flutter Apple Pay: [`applePayToken()`](https://github.com/flittpayments/flutter/blob/7bc950056d2242d315c349b26ae8319b1c2c9c8f/lib/src/cloudipsp.dart#L173)

- Flutter with card: [`payToken()`](https://github.com/flittpayments/flutter/blob/7bc950056d2242d315c349b26ae8319b1c2c9c8f/lib/src/cloudipsp.dart#L128)




## Backend SDKS

[Python](/sdk-and-mobile/sdk/python/)

[PHP](/sdk-and-mobile/sdk/php/)

[C#](/sdk-and-mobile/sdk/csharp/)

[Node.js](/sdk-and-mobile/sdk/nodejs/)

## Frontend SDKs

[JavaScript](/sdk-and-mobile/sdk/js/)

[Vue-js](/api/embedded-custom/)