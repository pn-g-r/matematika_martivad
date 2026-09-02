# Flutter SDK for Mobile(Android)

Getting Started

This project is a starting point for a Flutter [plug-in package](https://flutter.dev/developing-packages/), 
a specialized package that includes platform-specific implementation code for Android and/or iOS.

For help getting started with Flutter, view [online documentation](https://flutter.dev/docs), which offers tutorials, samples, guidance on mobile development, and a full API reference.

Flutter SDK allows you to accept payment from Visa/MasterCard, Apple Pay, Google Pay&trade; in any of your iOS and Android applications.

The latest version of the iOS SDK you can always find in our public repository

[https://github.com/flittpayments/flutter](https://github.com/flittpayments/flutter)

You can find demo app in [example](https://github.com/flittpayments/flutter/tree/main/example) directory

##Google Pay mobile application approval

1. Before integrating Flitt mobile SDK, register merchant in Flitt [Merchant Portal](https://portal.flitt.com) 
and request Flitt support support@flitt.com to enable Google Pay on your account. You will get a merchant ID in test mode.

2. Build your app using Flitt merchant ID in test mode with Flitt SDK. Flitt SDK will use `ENVIRONMENT_TEST` mode and

    ```
    gatewayMerchantId: <your Flitt merchant_id>
    gatewayID: flitt
    ```

3. Follow instructions to request Google for production access: [https://developers.google.com/pay/api/android/guides/test-and-deploy/publish-your-integration](https://developers.google.com/pay/api/android/guides/test-and-deploy/publish-your-integration)
4. Google will review the application according to its integration checklist and provide recommendations if necessary.
5. If all requirements are met, production access is granted.
6. Request Flitt support to switch your merchant ID to live with `ENVIRONMENT_PRODUCTION` mode.
7. Submit production APK pointing to live merchant ID to Google for approval.