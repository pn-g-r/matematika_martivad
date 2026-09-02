# iOS SDK (Swift)

iOS SDK allows you to accept payment from Visa/MasterCard and Apple Pay in any of your iOS applications.

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


**1 Initiate payment on backend and obtain payment token**

Create order at your server:
    
``` sh
curl -i -X POST \
 -H "Content-Type:application/json" \
 -d \
'{
  "request": {
    "server_callback_url": "http://myshop/callback/",
    "order_id": "TestOrder_JSSDK_v2",
    "currency": "GEL",
    "merchant_id": 1549901,
    "order_desc": "Test payment",
    "lifetime" : 999999,
    "amount": 1000,
    "signature": "91ea7da493a8367410fe3d7f877fb5e0ed666490"
  }
}' \
 'https://pay.flitt.com/api/checkout/token'
```

Receive payment token:

``` json    
    {
      "response":{
        "response_status":"success",
        "token":"b3c178ad84446ef36eaab365b1e12e6987e9b3d9"
      }
    }
```


**2 Define properties**


`PSCardInputView` is required to securely process card data inputs. Card data can't be obtained by application due to PCI DSS requirements.  
`PSCloudipspWKWebView` is required to redirect payer to webview during 3DSecure authentication.  
`PSCloudipspApi` is main class for payment initiation. 

``` java
@property (nonatomic, weak) IBOutlet PSCardInputView *cardInputView;
@property (nonatomic, strong) PSCloudipspWKWebView *webView;
@property (nonatomic, strong) PSCloudipspApi *api;
```

**3 Create layouts for card inputs**

```java
// LAYOUT FIELDS
self.cardNumberTextField = [[PSCardNumberTextField alloc] initWithFrame:CGRectMake(20, 8, 280, 30)];
self.cardNumberTextField.placeholder = @"Card Number";
[self.fields addObject:self.cardNumberTextField];

self.expMonthTextField = [[PSExpMonthTextField alloc] initWithFrame:CGRectMake(20, 46, 136, 30)];
self.expMonthTextField.placeholder = @"MM";
[self.fields addObject:self.expMonthTextField];

self.expYearTextField = [[PSExpYearTextField alloc] initWithFrame:CGRectMake(164, 46, 136, 30)];
self.expYearTextField.placeholder = @"YY";
[self.fields addObject:self.expYearTextField];

self.cvvTextField = [[PSCVVTextField alloc] initWithFrame:CGRectMake(20, 84, 280, 30)];
self.cvvTextField.placeholder = @"CVV";
[self.fields addObject:self.cvvTextField];

self.cardInputLayout = [[PSCardInputLayout alloc] initWithFrame:CGRectMake(0, 216, 320, 122)
                                            cardNumberTextField:self.cardNumberTextField
                                              expMonthTextField:self.expMonthTextField
                                               expYearTextField:self.expYearTextField
                                                   cvvTextField:self.cvvTextField];
[self.scrollView addSubview:self.cardInputLayout];
```

**4 Create layout for payment button**

```java
    // PAY CONTROL
    self.payButton = [[UIButton alloc] initWithFrame:CGRectMake(20, CGRectGetMaxY(self.cardInputLayout.frame), 280, 30)];
    [self.payButton setTitle:@"Pay" forState:UIControlStateNormal];
    [self.payButton setBackgroundColor:[UIColor colorWithRed:255.f/255.f green:204.f/255.f blue:102.f/255.f alpha:1.0]];
    self.payButton.layer.cornerRadius = 5.f;
    [self.payButton addTarget:self action:@selector(pay:) forControlEvents:UIControlEventTouchUpInside];
    [self.scrollView addSubview:self.payButton];
```    

**5 Setup 3DSecure webview**

```java
#pragma mark - Setup WebView
    
- (void)setupWebView {
    self.webView = [[PSCloudipspWKWebView alloc] initWithFrame:CGRectMake(0, 64, self.view.bounds.size.width, self.view.bounds.size.height - 66)];
    [self.view insertSubview:self.webView aboveSubview:self.scrollView];
}
```    

**6 Initialize PSCloudipspApi object**
``` java
self.api = [PSCloudipspApi apiWithMerchant:1396424 andCloudipspView:self.webView];
```

where `1396424` should be replaced with your MerchantID identifier from [Flitt Merchant Portal](https://portal.flitt.com)


**7 Process payment on pay button click using payment token obtained on step 1**

```java
- (IBAction)pay:(UIButton *)sender {
    PSCard *card = [self.cardInputLayout confirm:self];
    if (card != nil) {
        [self taskWillStarted];
        [self.api pay:card withToken:token andDelegate:self];
    }
}
```

**8 Process payment result from `PSReceipt` object**

``` java
#pragma mark - PayCallbackDelegate
    
    
- (void)onPaidProcess:(PSReceipt *)receipt {
    self.result = [NSString stringWithFormat:NSLocalizedString(@"PAID_STATUS_KEY", nil), [PSReceipt getStatusName:receipt.status], (long)receipt.paymentId];
    [self taskDidFinished];
    [self navigate];
    //for getting all response fields
    //[PSReceiptUtils dumpFields:receipt];
}
    
- (void)onPaidFailure:(NSError *)error {
    if ([error code] == PSPayErrorCodeFailure) {
        NSDictionary *info = [error userInfo];
        self.result = [NSString stringWithFormat:@"PayError. Code %@\nDescription: %@", [info valueForKey:@"error_code"], [info valueForKey:@"error_message"]];
    } else {
        self.result = [NSString stringWithFormat:@"Error: %@", [error localizedDescription]];
    }
    [self navigate];
    [self taskDidFinished];
}
```