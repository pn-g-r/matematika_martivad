# iOS SDK (Objective-C)

iOS SDK allows you to accept payment from Visa/MasterCard, Apple Pay, Google Pay in any of your iOS applications.

The latest version of the iOS SDK you can always find in our public repository

[https://github.com/flittpayments/ios-sdk](https://github.com/flittpayments/ios-sdk)

To run the sample of application, run the command

``` sh

git clone git@github.com:flittpayments/ios-sdk.git
cd ios-sdk/Example
pod install

```

iOS SDK is also available through CocoaPods. To install it, simply add the following line to your Podfile:

``` sh

pod 'Flitt'

```

Example for Objective-C you can find by the link [https://github.com/flittpayments/ios-sdk/tree/master/Example](https://github.com/flittpayments/ios-sdk/tree/master/Example)

Integrate SDK putting the generated MerchantID in 2 places

1. In XCode -> Target -> Capabilities -> Apple Pay -> Merchant IDS

    [![XCode]][XCode]{ width="400" align="left" }
    
    [XCode]: /static/img/applepay/iossdk.jpeg

2. In integration SDK set `merchant_id` received during registration in Flitt [Merchant Portal](https://portal.flitt.com) in constructor instead of test 1396424

    ```java
    - (void)viewDidLoad {
        [super viewDidLoad];

         self.api = [PSCloudipspApi apiWithMerchant:1396424 andCloudipspView:nil];
    }   
        
    ```

github line link: [https://github.com/flittpayments/ios-sdk/blob/master/Example/Cloudipsp/CDStartViewController.m#L24](https://github.com/flittpayments/ios-sdk/blob/master/Example/Cloudipsp/CDStartViewController.m#L24)