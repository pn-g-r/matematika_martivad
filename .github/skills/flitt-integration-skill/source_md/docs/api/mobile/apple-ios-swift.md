# iOS SDK (Swift)

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

Example for Swift you can find by the link [https://github.com/flittpayments/ios-sdk/tree/master/ExampleSwift](https://github.com/flittpayments/ios-sdk/tree/master/ExampleSwift)

Integrate SDK putting the generated MerchantID in 2 places

1. In XCode -> Target -> Capabilities -> Apple Pay -> Merchant IDS

    [![XCode]][XCode]{ width="400" align="left" }
    
    [XCode]: /static/img/applepay/iossdk.jpeg

2. In integration SDK set `merchant_id` received during registration in Flitt [Merchant Portal](https://portal.flitt.com) in constructor instead of test 900234

    ``` html

    <textField opaque="NO" contentMode="scaleToFill" contentHorizontalAlignment="left" contentVerticalAlignment="center" text="1396424" borderStyle="roundedRect" placeholder="Enter merchant id" textAlignment="natural" minimumFontSize="17" translatesAutoresizingMaskIntoConstraints="NO" id="8pz-e9-tsn">
        
    ```

    github line link: [https://github.com/flittpayments/ios-sdk/blob/master/ExampleSwift/ExampleSwift/Base.lproj/Main.storyboard#L19](https://github.com/flittpayments/ios-sdk/blob/master/ExampleSwift/ExampleSwift/Base.lproj/Main.storyboard#L19)